#!/usr/bin/env python
# coding: utf-8

import time


import math
import sys
import time
from collections import defaultdict

import brambox
import pandas as pd
import numpy as np
import torch
import torchvision.models.detection.mask_rcnn

from head_detection.vision import utils
from brambox.stat._matchboxes import match_det, match_anno
from brambox.stat import coordinates, mr_fppi, ap, pr, threshold, fscore, peak, lamr
import wandb
from torch.cuda.amp import autocast, GradScaler
import time


def check_empty_target(targets):
    for tar in targets:
        if len(tar['boxes']) < 1:
            return True
    return False


def train_one_epoch(model, optimizer, data_loader, device, epoch, print_freq):
    model.train()
    metric_logger = utils.MetricLogger(delimiter="  ")
    metric_logger.add_meter('lr', utils.SmoothedValue(window_size=1, fmt='{value:.6f}'))
    header = 'Epoch: [{}]'.format(epoch)

    iter_count = (epoch-1) * len(data_loader)
    wandb_log_interval = 400

    lr_scheduler = None
    if epoch == 1:
        warmup_factor = 1. / 1000
        warmup_iters = min(1000, len(data_loader) - 1)

        lr_scheduler = utils.warmup_lr_scheduler(optimizer, warmup_iters, warmup_factor)

    scaler = torch.cuda.amp.GradScaler() # AMP GradScaler 초기화


    for images, targets in metric_logger.log_every(data_loader, print_freq, header):

        torch.cuda.empty_cache()
        if check_empty_target(targets):
            continue

        images = list(image.to(device) for image in images)
        targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

        optimizer.zero_grad()
        with torch.cuda.amp.autocast(): # Auto mixed precision
            loss_dict = model(images, targets)

        losses = sum(loss for loss in loss_dict.values())

        # reduce losses over all GPUs for logging purposes
        loss_dict_reduced = utils.reduce_dict(loss_dict)
        losses_reduced = sum(loss for loss in loss_dict_reduced.values())

        loss_value = losses_reduced.item()

        if not math.isfinite(loss_value):
            print("Loss is {}, stopping training".format(loss_value))
            print(loss_dict_reduced)
            sys.exit(1)

        # Scaler를 사용하여 backward 및 optimizer.step
        scaler.scale(losses).backward()
        scaler.step(optimizer)
        scaler.update()
        if lr_scheduler is not None:
            lr_scheduler.step()

        metric_logger.update(loss=losses_reduced, **loss_dict_reduced)
        metric_logger.update(lr=optimizer.param_groups[0]["lr"])

        avg_loss = metric_logger.meters["loss"].global_avg
        avg_lr = metric_logger.meters["lr"].global_avg

        iter_count += 1
        # 💾 N iteration마다 wandb에 기록
        if wandb.run is not None and iter_count % wandb_log_interval == 0:
            wandb.log({
                "train_loss": avg_loss,
                "lr": avg_lr,
            }, step=iter_count)

    return metric_logger


def _get_iou_types(model):
    model_without_ddp = model
    if isinstance(model, torch.nn.parallel.DistributedDataParallel):
        model_without_ddp = model.module
    iou_types = ["bbox"]
    if isinstance(model_without_ddp, torchvision.models.detection.MaskRCNN):
        iou_types.append("segm")
    if isinstance(model_without_ddp, torchvision.models.detection.KeypointRCNN):
        iou_types.append("keypoints")
    return iou_types


def safe_div(x,y):
    if y == 0:
        return 0
    return x / y

def get_moda(det, anno, threshold=0.2, ignore=None):
    if ignore is None:
        ignore = anno.ignore.any()

    # dets_per_frame = anno.groupby('image').filter(lambda x: any(x['ignore'] == 0)) 안쓰이길래 주석처리
    # dets_per_frame = dets_per_frame.groupby('image').size().to_dict()

    # Other param for finding matched anno
    crit = coordinates.pdollar if ignore else coordinates.iou
    label = len({*det.class_label.unique(), *anno.class_label.unique()}) > 1
    matched_dets = match_det(det, anno, threshold, criteria=crit,
                            class_label=label, ignore=2 if ignore else 0)
    fp_per_im = matched_dets[matched_dets.fp==True].groupby('image').size().to_dict()
    tp_per_im = matched_dets[matched_dets.tp==True].groupby('image').size().to_dict()
    valid_anno = anno[anno.ignore == False].groupby('image').size().to_dict()

    # assert valid_anno.keys() == tp_per_im.keys()
    # 위 코드 대신 이미지 수 체크 정도로 바꾸는 게 좋음
    missing_tp_images = set(valid_anno.keys()) - set(tp_per_im.keys())
    if missing_tp_images:
        print(f"len(missing_tp_images): {len(missing_tp_images)}")

        print("missing_tp_images top10:")
        for img_id in sorted(missing_tp_images)[:10]:
            print(img_id)

    moda_ = []
    for k, _ in valid_anno.items():
        n_gt = valid_anno[k]
        tp = tp_per_im.get(k, 0)
        fp = fp_per_im.get(k, 0)
        # miss = n_gt-tp_per_im[k]
        miss = n_gt - tp
        # fp = fp_per_im[k]
        moda_.append(safe_div((miss+fp), n_gt))
    return 1 - np.mean(moda_)


def get_modp(det, anno, threshold=0.2, ignore=None):
    if ignore is None:
        ignore = anno.ignore.any()
    # Compute TP/FP
    if not {'tp', 'fp'}.issubset(det.columns):
        crit = coordinates.pdollar if ignore else coordinates.iou
        label = len({*det.class_label.unique(), *anno.class_label.unique()}) > 1
        det = match_anno(det, anno, threshold, criteria=crit, class_label=label, ignore=2 if ignore else 0)
    elif not det.confidence.is_monotonic_decreasing:
        det = det.sort_values('confidence', ascending=False)
    modp = det.groupby('image')['criteria'].mean().mean()
    return modp

@torch.no_grad()
def evaluate(model, data_loader, out_path=None, benchmark=None):
    """
    Evaluates a model over testing set, using AP, Log MMR, F1-score
    """
    n_threads = torch.get_num_threads() # Pytorch가 사용하는 스레드 수 확인
    torch.set_num_threads(1) # 스레드 수를 1로 제한
    device=torch.device('cuda')
    cpu_device = torch.device("cpu")
    model.eval()
    metric_logger = utils.MetricLogger(delimiter="  ")
    header = 'Valid:'

    # Brambox eval related
    pred_dict = defaultdict(list)
    gt_dict = defaultdict(list)
    results = {}
    start_time = time.time()
    total_frames = 0
    for i, (images, targets) in enumerate(metric_logger.log_every(data_loader, 100, header)):
        images = list(img.to(device) for img in images)
        total_frames += len(images)

        torch.cuda.synchronize()
        model_time = time.time()
        # outputs = model(images)

        # mixed precision inference 수행
        with autocast():
            outputs = model(images)

        torch.cuda.synchronize()
        model_time = time.time() - model_time

        outputs = [{k: v.to(cpu_device) for k, v in t.items()} for t in outputs]
        model_time = time.time() - model_time
        evaluator_time = time.time()
        # Pred lists
        pred_boxes = [p['boxes'].numpy() for p in outputs]
        pred_scores = [p['scores'].numpy() for p in outputs]

        # GT List
        gt_boxes = [gt['boxes'].numpy()for gt in targets]

        # Just to be sure target and prediction have batchsize 2
        assert len(gt_boxes) == len(pred_boxes)
        for j in range(len(gt_boxes)):

            # im_name = str(targets[j]['image_id']) + '.jpg'
            im_name = str(targets[j]['image_id'])

            # write to results dict for MOT format
            # results[targets[j]['image_id'].item()] = {'boxes': pred_boxes[j],
            #                                           'scores': pred_scores[j]}
            results[targets[j]['image_id']] = {'boxes': pred_boxes[j],
                                                      'scores': pred_scores[j]}
            # print(results[targets[j]['image_id']])
            for _, (p_b, p_s) in enumerate(zip(pred_boxes[j], pred_scores[j])):
                pred_dict['image'].append(im_name)
                pred_dict['class_label'].append('head')
                pred_dict['id'].append(0)
                pred_dict['x_top_left'].append(p_b[0])
                pred_dict['y_top_left'].append(p_b[1])
                pred_dict['width'].append(p_b[2] - p_b[0])
                pred_dict['height'].append(p_b[3] - p_b[1])
                pred_dict['confidence'].append(p_s)

            for gt_b in gt_boxes[j]:
                gt_dict['image'].append(im_name)
                gt_dict['class_label'].append('head')
                gt_dict['id'].append(0)
                gt_dict['x_top_left'].append(gt_b[0])
                gt_dict['y_top_left'].append(gt_b[1])
                gt_dict['width'].append(gt_b[2] - gt_b[0])
                gt_dict['height'].append(gt_b[3] - gt_b[1])

        evaluator_time = time.time() - evaluator_time
        metric_logger.update(model_time=model_time, evaluator_time=evaluator_time)
    
    # Save results in MOT format if out_path is provided
    if out_path is not None:
        data_loader.dataset.write_results_files(results, out_path)
    # gather the stats from all processes
    pred_df = pd.DataFrame(pred_dict)
    gt_df = pd.DataFrame(gt_dict)
    pred_df['image'] = pred_df['image'].astype('category')
    gt_df['image'] = gt_df['image'].astype('category')

    # 좌표 및 confidence 등 주요 수치형 컬럼들 float64로 강제 변환
    for col in ['x_top_left', 'y_top_left', 'width', 'height', 'confidence']:
        if col in pred_df.columns:
            pred_df[col] = pred_df[col].astype('float64')
        if col in gt_df.columns:
            gt_df[col] = gt_df[col].astype('float64')

    gt_df['ignore'] = False
    pr_ = pr(pred_df, gt_df, ignore=False)

    ap_ = ap(pr_)
    mr_fppi_ = mr_fppi(pred_df, gt_df, threshold=0.5)
    lamr_ = lamr(mr_fppi_)
    f1_ = fscore(pr_)
    f1_ = f1_.fillna(0)
    threshold_ = peak(f1_)

    moda = get_moda(pred_df, gt_df, threshold=0.2, ignore=True)
    modp = get_modp(pred_df, gt_df, threshold=0.2, ignore=True)

    # FPS 계산
    total_time = time.time() - start_time
    fps = total_frames / total_time

    result_dict = {
        'AP' : ap_,
        'Log-average miss rate' : lamr_,
        'F1' : threshold_.f1,
        'Recall':pr_['recall'].values[-1],
        'Precision': pr_['precision'].values[-1],
        'moda(Multiple object detection accuracy)' : moda,
        'modp(Multiple object detection precision)' : modp,
        'FPS': fps,
                    }

    if wandb.run is not None:  # wandb.init() 했는지 체크
        wandb.log(result_dict)

    metric_logger.synchronize_between_processes()

    torch.set_num_threads(n_threads)
    return result_dict
