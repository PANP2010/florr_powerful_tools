"""
优化训练脚本 - 从上次进度继续，使用MPS加速
"""

import torch
from ultralytics import YOLO
from pathlib import Path


def get_device():
    if torch.backends.mps.is_available():
        print("✓ 使用 Apple MPS 加速")
        return 'mps'
    elif torch.cuda.is_available():
        print("✓ 使用 CUDA 加速")
        return 'cuda'
    else:
        print("使用 CPU 训练")
        return 'cpu'


def continue_training():
    print("=" * 60)
    print("优化训练 - 从上次进度继续 (MPS加速)")
    print("=" * 60)
    
    device = get_device()
    
    checkpoint_path = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/runs/mob_detector_v3_mps/weights/last.pt")
    
    if checkpoint_path.exists():
        print(f"\n从checkpoint继续训练: {checkpoint_path}")
        model = YOLO(str(checkpoint_path))
    else:
        print("\n未找到checkpoint，从头开始训练")
        model = YOLO('yolov8n.pt')
    
    data_yaml = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/synthetic_mobs_v3/data.yaml")
    
    print(f"数据集配置: {data_yaml}")
    print(f"设备: {device}")
    
    print("\n开始继续训练...")
    results = model.train(
        data=str(data_yaml),
        epochs=50,
        imgsz=640,
        batch=32,
        name='mob_detector_v3_mps',
        project='/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/runs',
        device=device,
        patience=10,
        save=True,
        plots=True,
        resume=False,
        optimizer='AdamW',
        lr0=0.001,
        lrf=0.01,
        momentum=0.9,
        weight_decay=0.0005,
        warmup_epochs=3,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        box=7.5,
        cls=0.5,
        dfl=1.5,
        pose=12.0,
        kobj=1.0,
        label_smoothing=0.0,
        nbs=64,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=0.0,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.0,
        copy_paste=0.0,
        workers=4,
    )
    
    print("\n✓ 训练完成!")
    print(f"最佳模型: {results.save_dir / 'weights' / 'best.pt'}")
    
    return results


if __name__ == '__main__':
    continue_training()
