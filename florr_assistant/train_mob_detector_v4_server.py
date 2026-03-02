"""
高质量模型训练脚本 V4 - Ubuntu 双卡 3090 服务器版
支持 CUDA 多卡 DDP 训练
"""

import torch
from ultralytics import YOLO
from pathlib import Path
import argparse


def train(data_yaml: str, epochs: int = 80, batch: int = 64, imgsz: int = 640):
    print("=" * 60)
    print("高质量模型训练 V4 - 双卡 3090")
    print("=" * 60)
    
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA 不可用，请检查 GPU 环境")
    
    gpu_count = torch.cuda.device_count()
    print(f"✓ 检测到 {gpu_count} 张 GPU")
    for i in range(gpu_count):
        print(f"  - GPU {i}: {torch.cuda.get_device_name(i)}")
    
    data_path = Path(data_yaml)
    if not data_path.exists():
        raise FileNotFoundError(f"数据集配置文件不存在: {data_path}")
    
    print(f"\n数据集配置: {data_path}")
    
    model = YOLO('yolov8n.pt')
    
    effective_batch = batch * gpu_count
    print(f"\n单卡 batch: {batch}, 总 batch: {effective_batch}")
    print(f"训练参数: epochs={epochs}, imgsz={imgsz}")
    
    print("\n开始训练...")
    results = model.train(
        data=str(data_path),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name='mob_detector_v4',
        project='./runs',
        device=[0, 1],
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
        workers=8,
        amp=True,
        close_mosaic=10,
        freeze=0,
    )
    
    print("\n✓ 训练完成!")
    print(f"最佳模型: {results.save_dir / 'weights' / 'best.pt'}")
    
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='训练 YOLOv8 怪物检测模型')
    parser.add_argument('--data', type=str, default='./data.yaml', help='数据集配置文件路径')
    parser.add_argument('--epochs', type=int, default=80, help='训练轮数')
    parser.add_argument('--batch', type=int, default=64, help='单卡 batch size')
    parser.add_argument('--imgsz', type=int, default=640, help='图像尺寸')
    
    args = parser.parse_args()
    
    train(
        data_yaml=args.data,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
    )
