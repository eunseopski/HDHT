# config/det_cfg.py

det_cfg = {
    'backbone': 'resnet50',
    'trained_model': 'model/FT_R50_epoch_24.pth',
    'confidence_threshold': 0.1,
    'nms_threshold': 0.5,
    'use_deform': False,
    'context': 'cpm',
    'default_filter': False,
    'cpmfeat_dim': 1024,
    'median_anchor': True,
    'upscale_rpn': False,
    'benchmark': 'Combined'
}

