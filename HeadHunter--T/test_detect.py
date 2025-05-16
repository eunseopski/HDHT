# Test HeadHunter detector

import yaml
from head_detection.data import cfg_mnet, cfg_res50_4fpn, cfg_res152
from obj_detect import HeadHunter
import os.path as osp
from glob import glob
from matplotlib.pyplot import imread
from tqdm import tqdm
import cv2
import time
import pdb


##########################################
# Load video

im_shape = (1080, 1920, 3)
im_path = '/home/choi/hwang/workspace/HeadHunter/datasets/CroHD/test/HT21-11/img1'

seq_images = sorted(glob(osp.join(im_path, '*'+'.jpg')))


##########################################
# Load detector
cfg_file = './config/config.yaml'

with open(cfg_file, 'r') as stream:
    CONFIG = yaml.safe_load(stream)
det_cfg = CONFIG['DET']['det_cfg']
backbone = CONFIG['DET']['backbone']

# Initialise network configurations
if backbone == 'resnet50':
    net_cfg = cfg_res50_4fpn
elif backbone == 'resnet152':
    net_cfg = cfg_res152
elif backbone == 'mobilenet':
    net_cfg = cfg_mnet
else:
    raise ValueError("Invalid Backbone")

detector = HeadHunter(net_cfg, det_cfg, im_shape, im_path).cuda()


##########################################
# Detect

# number of frames to compute fps
num_frames = 30

# initialize fps computation
count = 0
start = time.time()

for im in tqdm(seq_images):
    # fps computation
    if count == num_frames:
        end = time.time()
        seconds = end - start
        fps = num_frames / seconds
        print('Time taken = {0} seconds'.format(seconds))
        print('FPS = {0}'.format(fps))
        count = 0
        start = time.time()

    # network forwarding
    cur_im = imread(im)
    boxes, scores = detector.predict_box(cur_im)

    plotting_im = cur_im.copy()
    plotting_im = cv2.cvtColor(plotting_im, cv2.COLOR_BGR2RGB)
    for i in range(boxes.shape[0]):
        box = [int(b) for b in boxes[i]]
        cv2.rectangle(plotting_im, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

    cv2.imshow('img', plotting_im)
    ret = cv2.waitKey(1)
    if ret == 27:
        break

    count = count + 1

# destroy all windows
cv2.destroyAllWindows()


