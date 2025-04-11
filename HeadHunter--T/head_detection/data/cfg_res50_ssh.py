from easydict import EasyDict as edict

__C = edict()
cfg_res50 = __C

# 기존 설정
__C.NET = 'resnet50'
__C.CONV_BODY = 'R-50'
__C.FPN = True
__C.SSH = False

# 누락된 필수 설정
__C.name = 'Resnet50'  # create_backbone()에서 사용
__C.in_channel = 256  # ResNet의 초기 conv 출력 채널 수
__C.out_channel = 256  # FPN 출력 채널 수 (모델에 따라 조정 가능)

# return_layers: backbone에서 어떤 layer의 출력을 사용할지 설정
__C.return_layers = {
    'layer1': 0,  # 추가!
    'layer2': 1,
    'layer3': 2,
    'layer4': 3
}

__C.pretrain = True  # torchvision pretrained 모델 사용 여부

