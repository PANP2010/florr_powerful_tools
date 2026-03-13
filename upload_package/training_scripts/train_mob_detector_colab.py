"""
YOLOv8s Mob 检测器训练脚本 - 适用于免费 GPU 平台
支持: Google Colab, Kaggle Kernels
"""

import torch
from ultralytics import YOLO
from pathlib import Path
import argparse
import os


def get_device():
    if torch.cuda.is_available():
        print(f"✓ 使用 CUDA 加速: {torch.cuda.get_device_name(0)}")
        print(f"  显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        return 'cuda'
    elif torch.backends.mps.is_available():
        print("✓ 使用 Apple MPS 加速")
        return 'mps'
    else:
        print("使用 CPU 训练")
        return 'cpu'


def train(data_yaml: str, epochs: int = 100, batch: int = 16, imgsz: int = 640, 
          project: str = './runs', name: str = 'mob_detector_yolov8s'):
    print("=" * 60)
    print("YOLOv8s Mob 检测器训练")
    print("=" * 60)
    
    device = get_device()
    
    data_path = Path(data_yaml)
    if not data_path.exists():
        raise FileNotFoundError(f"数据集配置文件不存在: {data_path}")
    
    print(f"\n数据集配置: {data_path}")
    
    model = YOLO('yolov8s.pt')
    
    print(f"\n训练参数:")
    print(f"  - 模型: YOLOv8s")
    print(f"  - Epochs: {epochs}")
    print(f"  - Batch size: {batch}")
    print(f"  - Image size: {imgsz}")
    print(f"  - Device: {device}")
    
    print("\n开始训练...")
    results = model.train(
        data=str(data_path),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name=name,
        project=project,
        device=device,
        patience=20,
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
        amp=True,
        close_mosaic=10,
    )
    
    print("\n✓ 训练完成!")
    best_model_path = Path(results.save_dir) / 'weights' / 'best.pt'
    print(f"最佳模型: {best_model_path}")
    
    print("\n验证模型...")
    metrics = model.val()
    print(f"mAP50: {metrics.box.map50:.4f}")
    print(f"mAP50-95: {metrics.box.map:.4f}")
    
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='训练 YOLOv8s 怪物检测模型')
    parser.add_argument('--data', type=str, required=True, help='数据集配置文件路径 (data.yaml)')
    parser.add_argument('--epochs', type=int, default=100, help='训练轮数 (默认: 100)')
    parser.add_argument('--batch', type=int, default=16, help='Batch size (默认: 16)')
    parser.add_argument('--imgsz', type=int, default=640, help='图像尺寸 (默认: 640)')
    parser.add_argument('--project', type=str, default='./runs', help='项目保存路径')
    parser.add_argument('--name', type=str, default='mob_detector_yolov8s', help='实验名称')
    
    args = parser.parse_args()
    
    train(
        data_yaml=args.data,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        project=args.project,
        name=args.name,
    )
