_base_ = [
    '/opt/ml/level2_semanticsegmentation_cv-level2-cv-03/mmsegmentation/configs/_base_/models/upernet_convnext.py',
    '/opt/ml/level2_semanticsegmentation_cv-level2-cv-03/CV03/configs/Augmentation/Aug_NCmx.py', 
    '/opt/ml/level2_semanticsegmentation_cv-level2-cv-03/mmsegmentation/configs/_base_/default_runtime.py',
    '/opt/ml/level2_semanticsegmentation_cv-level2-cv-03/CV03/_base_/scheduler_epochs_60.py'
]
import wandb

crop_size = (640, 640)
checkpoint_file = 'https://download.openmmlab.com/mmclassification/v0/convnext/downstream/convnext-xlarge_3rdparty_in21k_20220301-08aa5ddc.pth'  # noqa
model = dict(
    backbone=dict(
        type='mmcls.ConvNeXt',
        arch='xlarge',
        out_indices=[0, 1, 2, 3],
        drop_path_rate=0.4,
        layer_scale_init_value=1.0,
        gap_before_final_norm=False,
        init_cfg=dict(
            type='Pretrained', checkpoint=checkpoint_file,
            prefix='backbone.')),
    decode_head=dict(
        in_channels=[256, 512, 1024, 2048],
        num_classes=11,
    ),
    auxiliary_head=dict(in_channels=1024, num_classes=11),
    test_cfg=dict(mode='slide', crop_size=crop_size, stride=(426, 426)),
)

optimizer = dict(
    constructor='LearningRateDecayOptimizerConstructor',
    _delete_=True,
    type='AdamW',
    lr=0.00008,
    betas=(0.9, 0.999),
    weight_decay=0.05,
    paramwise_cfg={
        'decay_rate': 0.9,
        'decay_type': 'stage_wise',
        'num_layers': 12
    })

lr_config = dict(
    _delete_=True,
    policy='poly',
    warmup='linear',
    warmup_iters=1500,
    warmup_ratio=1e-6,
    power=1.0,
    min_lr=0.0,
    by_epoch=False)

# By default, models are trained on 8 GPUs with 2 images per GPU
data = dict(samples_per_gpu=4)
# fp16 settings
optimizer_config = dict(type='Fp16OptimizerHook', loss_scale='dynamic')
# fp16 placeholder
fp16 = dict()
runner = dict(type='EpochBasedRunner', max_epochs=60)
checkpoint_config = dict(interval=1, max_keep_ckpts=3)
evaluation = dict(interval=1, metric='mIoU', pre_eval=True,save_best='mIoU')


wandb.login()
# yapf:disable
log_config = dict(
    interval=100,
    hooks=[
        dict(type='TextLoggerHook', by_epoch=True),
        dict(type='WandbLoggerHook',interval=100,
            init_kwargs=dict(
                project='Segmentation_project',
                entity = 'aitech4_cv3',
                name = "Covnext_Aug_NCmx"),)
        # log_checkpoint=True,
        # log_checkpoint_metadata=True,
        # dict(type='TensorboardLoggerHook')
        # dict(type='PaviLoggerHook') # for internal services
    ])
