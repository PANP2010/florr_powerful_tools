"""
高质量模型训练脚本 V4
使用更多数据、更小怪物尺寸训练
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


def train():
    print("=" * 60)
    print("高质量模型训练 V4")
    print("=" * 60)
    
    device = get_device()
    
    data_yaml = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/synthetic_mobs_v4/data.yaml")
    
    print(f"\n数据集配置: {data_yaml}")
    
    model = YOLO('yolov8n.pt')
    
    print("\n开始训练...")
    results = model.train(
        data=str(data_yaml),
        epochs=80,
        imgsz=640,
        batch=32,
        name='mob_detector_v4',
        project='/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/runs',
        device=device,
        patience=15,
        save=True,
        plots=True,
        optimizer='AdamW',
        lr0=0.001,
        lrf=0.01,
        weight_decay=0.0005,
        warmup_epochs=3,
        box=7.5,
        cls=0.5,
        dfl=1.5,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        translate=0.1,
        scale=0.5,
        fliplr=0.5,
        mosaic=1.0,
        workers=4,
    )
    
    print("\n✓ 训练完成!")
    print(f"最佳模型: {results.save_dir / 'weights' / 'best.pt'}")
    
    return results


if __name__ == '__main__':
    train()
