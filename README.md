# Head Detector

Code for the head detector (HeadHunter) proposed in our CVPR 2021 paper `Tracking Pedestrian Heads in Dense Crowd`. The `head_detection` module can be installed using `pip` in order to be able to plug-and-play with HeadHunter-T.

## Requirements

1. Nvidia Driver >= 418

2. Cuda 10.0 and compaitible CudNN

3. Python packages : To install the required python packages;
	`conda env create -f head_detection.yml`.

4. Use the anaconda environment `head_detection` by activating it, `source activate head_detection` or `conda activate head_detection`.

5. Alternatively pip can be used to install required packages using `pip install -r requirements.txt` or update your existing environment with the aforementioned yml file.


## Config file
A config file is necessary for all training. It's built to ease the number of arg variable passed during each execution. Each sub-sections are as elaborated below.

1. DATASET
    1. Set the `base_path` as the parent directory where the dataset is situated at.
    2. Train and Valid are `.txt` files that contains relative path to respective images from the `base_path` defined above and their corresponding Ground Truth in `(x_min, y_min, x_max, y_max)` format. Generation files for the three datasets can be seen inside `data` directory. For example, 
    ```
    /path/to/image.png
    x_min_1, y_min_1, x_max_1, y_max_1
    x_min_2, y_min_2, x_max_2, y_max_2
    x_min_3, y_min_3, x_max_3, y_max_3
    .
    .
    .
    ```
    3. `mean_std` are RGB means and stdev of the training dataset. If not provided, can be computed prior to the start of the training
2. TRAINING
    1. Provide `pretrained_model` and corresponding `start_epoch` for resuming.
    2. `milestones` are epoch at which the learning rates are set to `0.1 * lr`.
    3. `only_backbone` option loads just the Resnet backbone and not the head. Not applicable for mobilenet.

3. NETWORK
    1. The mentioned parameters are as described in experiment section of the paper.
    2. When using `median_anchors`, the anchors have to be defined in `anchors.py`.
    3. We experimented with mobilenet, resnet50 and resnet150 as alternative backbones. This experiment was not reported in the paper due to space constraints. We found the accuracy to significantly decrease with mobilenet but resnet50 and resnet150 yielded an almost same performance.
    4. We also briefly experimented with Deformable Convolutions but again didn't see noticable improvements in performance. The code we used are available in this repository.

### Note : 
This codebase borrows a noteable portion from pytorch-vision owing to the fact some of their modules cannot be "imported" as a package. 

## 데이터셋
crowdhuman 데이터셋은 test data가 없음.
```
datasets/
├── CroHD/
│   ├── test/
│   	└── ...
│   └── train/
│   	└── ...
├── test/
│   ├── 1_scut_head.txt
│   └── ~.jpg
├── train/
│   ├── 1_train.txt
│   ├── 1_scut_head.txt
│   ├── 1_crowdhuman.txt
│   └── ~.jpg # (crowdhuman + scut_head)
├── valid/
│   ├── 1_valid.txt
│   ├── 1_scut_head.txt
│   ├── 1_crowdhuman.txt
│   └── ~.jpg # (crowdhuman + scut_head)
```

## Instructions Detection

1. 학습시 코드
	
	```
	python -m torch.distributed.launch --nproc_per_node=1 --use_env train.py --cfg_file <yaml파일 경로> --world_size 1 --num_workers 4
	```
2. evaluate 코드 (성능 평가)
	```
	python evaluate.py --test_dataset <txt파일 경로> --pretrained_model <pth파일 경로> --exp_name <실험 이름> --context cpm --upscale_rpn False
	```


## Instructions Tracking

1. Tracking test 코드 (bbox 시각화)

	```
	python run_mot.py --base_dir /path/to/CroHD/ --cfg_file <your config file> --dataset <test/train> --save_path <directory where results in MOT format can be saved>
	``` 

2. Tracking test 코드 (MOTchallenge 형식의 결과 출력)
	```
	python run_new.py --base_dir /path/to/frames --save_dir /path/to/save/tracks 
	```
3. To evaluate the MOT tracking accuracies based on existing metrics and the proposed IDEucl metric,

	```
	python evaluation.py --gt_dir /path/to/training/gt --pred_dir /path/to/prediction
	```




 

## Citation :

```
@InProceedings{Sundararaman_2021_CVPR,
    author    = {Sundararaman, Ramana and De Almeida Braga, Cedric and Marchand, Eric and Pettre, Julien},
    title     = {Tracking Pedestrian Heads in Dense Crowd},
    booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
    month     = {June},
    year      = {2021},
    pages     = {3865-3875}
}
```


