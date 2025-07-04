#!/usr/bin/env python
# coding: utf-8

import csv
import os
import os.path as osp
from collections import defaultdict
from pathlib import Path

import albumentations as A
import numpy as np
import torch
import torch.utils.data as data
from albumentations import BboxParams, Compose, HorizontalFlip
from albumentations.pytorch import ToTensorV2
from torchvision.ops.boxes import clip_boxes_to_image
from torchvision.transforms.functional import to_tensor

# try:
#     from scipy.misc import imread
# except ImportError:
#     from scipy.misc.pilutil import imread
import imageio
class HeadDataset(data.Dataset):
    """
    Dataset class.
    """
    def __init__(self, txt_path, base_path, dataset_param, train=True):
        self.base_path = base_path # txt 파일의 경로
        self.bboxes = defaultdict(list)
        self.mean = dataset_param.get('mean', None)
        self.std = dataset_param.get('std', None)
        self.shape = dataset_param.get('shape', (800, 800))
        with open(osp.join(base_path, txt_path), 'r') as txt:
            lines = txt.readlines()
            self.imgs_path = [i.rstrip().strip("#").lstrip() 
                              for i in lines if i.startswith('#')]
            ind = -1
            for lin in lines:
                if lin.startswith('#'): # #으로 시작한 건 이미지 주소이기 때문에 건너 뜀
                    ind+=1
                    continue
                lin_list = [float(i) for i in lin.rstrip().split(',')] # bbox 정보 얻기
                self.bboxes[ind].append(lin_list)
        self.is_train = train
        self.transforms = self.get_transform() #증강 함수

    def __len__(self):
        return len(self.imgs_path)

    def filter_targets(self, boxes, im):
        """
        Remove boxes with negative area
        """
        filtered_targets = []
        for bx in boxes:
            clipped_im = clip_boxes_to_image(torch.tensor(bx), im.shape[:2]).cpu().numpy()
            area_cond = self.get_area(clipped_im) <= 1
            dim_cond = clipped_im[2] - clipped_im[0] <= 0 and clipped_im[3] - clipped_im[1] <= 0
            # if width_cond or height_cond or area_cond or dim_cond:
            if area_cond or dim_cond:
                continue
            filtered_targets.append(clipped_im)
        return np.array(filtered_targets)


    def get_area(self, boxes):
        """
        Area of BB
        """
        boxes = np.array(boxes)
        if len(boxes.shape) != 2:
            area = np.product(boxes[2:4] - boxes[0:2])
        else:
            area = np.product(boxes[:, 2:4] - boxes[:, 0:2], axis=1)
        return area


    def get_transform(self):
        transforms = []
        if self.is_train:
            transforms.extend([
                      # A.RandomSizedBBoxSafeCrop(width=self.shape[0],
                      #                           height=self.shape[1],
                      #                           erosion_rate=0., p=0.2),

                    A.LongestMaxSize(max_size=1000, p=1.0),
                    A.PadIfNeeded(min_height=600, min_width=1000, border_mode=0, value=0, p=1.0),
                    A.RGBShift(),
                    A.RandomBrightnessContrast(p=0.5),
                    A.HorizontalFlip(p=0.5),
                    ])

        # transforms.append(ToTensorV2())
        composed_transform = Compose(transforms,
                                     bbox_params=BboxParams(format='pascal_voc',
                                                            min_area=0,
                                                            min_visibility=0,
                                                            label_fields=['labels']))
        return composed_transform


    
    def refine_transformation(self, transformed_dict):
        """
        Change keys of the target dictionary compaitable with Pytorch
        Albumnation uses images, bboxes, labels differently from Pytorch.
        This method reverts such transformation
        """
        transf_box = transformed_dict.pop('bboxes')
        transf_labels = transformed_dict.pop('labels')

        img = transformed_dict.pop('image')
        if not isinstance(transf_box, torch.Tensor):
            transf_box = torch.tensor(np.array(transf_box),
                                      dtype=torch.float32)
        transformed_dict['boxes'] = transf_box

        if not isinstance(transf_labels, torch.Tensor):
            transformed_dict['labels'] = torch.tensor(np.array(transf_labels),
                                                      dtype=torch.int64)

        return img, transformed_dict


    def create_target_dict(self, img, target, index):
        """
        Create the GT dictionary in similar style to COCO.
        For empty boxes, use [1,2,3,4] as box dimension, but with
        background class label. Refer to __getitem__ comment.
        """
        n_target = len(target)
        image_id = torch.tensor([index])

        # When there are no targets, set the BBOxes to 1pixel wide
        # and assign background label
        if n_target == 0:
            target, n_target = [[1, 2, 3, 4]], 1
            boxes = torch.tensor(target, dtype=torch.float32)
            labels = torch.zeros((n_target,), dtype=torch.int64)

        else:
            boxes = torch.tensor(target, dtype=torch.float32)
            labels = torch.ones((n_target,), dtype=torch.int64)

        area = torch.tensor(self.get_area(target))

        target_dict = {
                        'image' : img,
                        'bboxes': boxes,
                        'labels': labels.tolist(),
                        'image_id': image_id,
                        }

        return target_dict


    def __getitem__(self, index):
        """
        This iterator is written in a very hacky way as Pytorch cannot handle
        cases when there are no GT boxes present. Hence, when there are no GT,
        pass a new Box as 0s.

        Furthermore, as there are log operation in RPN, empty box or one with 0 area
        results in log(0) leading to NAN while training. Hence, boxes are to be
        [[1,2,3,4]] rather than [[0,0,0,0]]. Pytorch is aware of this issue, but will
        not fix them. 
        https://discuss.pytorch.org/t/torchvision-faster-rcnn-empty-training-images/46935
        """
        img_path = osp.join(self.base_path, self.imgs_path[index])

        img = imageio.imread(img_path)
        labels = self.bboxes[index]
        annotations = np.zeros((0, 4))

        if len(labels) == 0:
            label = [[0, 0, 0, 0, 0]]
        ignore_ar = []
        for idx, label in enumerate(labels):
            annotation = np.zeros((1, 4))
            # bbox
            annotation[0, 0] = label[0]  # x1
            annotation[0, 1] = label[1]  # y1
            annotation[0, 2] = label[2]  # x2
            annotation[0, 3] = label[3]  # y2
            annotations = np.append(annotations, annotation, axis=0)

        target = self.filter_targets(annotations, img)

        # Preprocess (Data augmentation)
        target_dict = self.create_target_dict(img, target, index)

        # target_dict.pop('ignore', None)  # 'ignore' 키 있으면 삭제, 없으면 무시
        transformed_dict = self.transforms(
            image=target_dict["image"],
            bboxes=target_dict["bboxes"],
            labels=target_dict["labels"]
        )
        transformed_dict["image"] = to_tensor(transformed_dict["image"])

        # Replace keys compaitible with Torch's FRCNN
        img, target = self.refine_transformation(transformed_dict)
        if not self.is_train:
            target["image_id"] = os.path.basename(img_path)

        return img, target


    def write_results_files(self, results, output_dir):
        """Write the detections in the format for MOT17Det sumbission

        Credits : Tim Meinhardt
        """

        #format_str = "{}, -1, {}, {}, {}, {}, {}, -1, -1, -1"

        files = {}
        for image_id, res in results.items():
            path = Path(self.imgs_path[image_id])
            # HeadHunter/test/MOT1904/img/000001.jpg -> MOT1904, 000001
            seq_name, frame = path.parts[-3], int(path.parts[-1].split('.')[0])
            # Now get the output name of the file
            out = seq_name + '.txt'
            outfile = osp.join(output_dir, out)

            # check if out in keys and create empty list if not
            if outfile not in files.keys():
                files[outfile] = []

            for box, score in zip(res['boxes'], res['scores']):
                x1 = box[0].item()
                y1 = box[1].item()
                x2 = box[2].item()
                y2 = box[3].item()
                files[outfile].append(
                    [frame, -1, x1, y1, x2 - x1, y2 - y1, score.item(), -1, -1, -1])

        for k, v in files.items():
            with open(k, "w") as of:
                writer = csv.writer(of, delimiter=',')
                for d in v:
                    writer.writerow(d)
