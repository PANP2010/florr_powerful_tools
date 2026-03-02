"""
继续训练YOLO怪物检测模型 V3 - 使用MPS加速
从上次保存的checkpoint继续训练
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
    print("继续训练YOLO怪物检测模型 V3 (MPS加速)")
    print("=" * 60)
    
    device = get_device()
    
    checkpoint_path = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/runs/mob_detector_v3_mps/weights/best.pt")
    
    if checkpoint_path.exists():
        print(f"\n从最佳模型加载: {checkpoint_path}")
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
        epochs=100,
        imgsz=640,
        batch=16,
        name='mob_detector_v3_mps',
        project='/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/runs',
        device=device,
        patience=15,
        save=True,
        plots=True,
        resume=False,
        augment=True,
        degrees=0,
        scale=0,
        flipud=0.3,
        fliplr=0.3
    )
    
    print("\n✓ 训练完成!")
    print(f"最佳模型: {results.save_dir / 'weights' / 'best.pt'}")
    
    return results


if __name__ == '__main__':
    continue_training()
