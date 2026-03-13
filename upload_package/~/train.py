"""
高质量模型训练脚本 V5 - 双卡 3090 服务器版
- 300 轮训练
- 防过拟合优化
- 支持 CUDA 多卡 DDP 训练
"""

import torch
from ultralytics import YOLO
from pathlib import Path
import argparse
import json
from datetime import datetime


def train(data_yaml: str, 
          epochs: int = 300, 
          batch: int = 32, 
          imgsz: int = 640,
          resume: str = None):
    print("=" * 60)
    print("高质量模型训练 V5 - 双卡 3090")
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
    
    if resume:
        print(f"\n从检查点恢复训练: {resume}")
        model = YOLO(resume)
    else:
        print("\n使用预训练模型: yolov8n.pt")
        model = YOLO('yolov8n.pt')
    
    effective_batch = batch * gpu_count
    print(f"\n单卡 batch: {batch}, 总 batch: {effective_batch}")
    print(f"训练参数: epochs={epochs}, imgsz={imgsz}")
    
    print("\n防过拟合策略:")
    print("  - Dropout: 0.2")
    print("  - Weight Decay: 0.001")
    print("  - 数据增强: HSV, 翻转, 缩放, 平移")
    print("  - Mosaic 增强: 最后 20 轮关闭")
    print("  - 早停: patience=30")
    print("  - 学习率调度: Cosine Annealing")
    
    print("\n开始训练...")
    results = model.train(
        data=str(data_path),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name='mob_detector_v5',
        project='./runs',
        device=[0, 1],
        
        patience=30,
        save=True,
        save_period=10,
        plots=True,
        
        optimizer='AdamW',
        lr0=0.002,
        lrf=0.0001,
        momentum=0.937,
        weight_decay=0.001,
        warmup_epochs=5,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        
        box=7.5,
        cls=0.5,
        dfl=1.5,
        dropout=0.2,
        
        hsv_h=0.02,
        hsv_s=0.8,
        hsv_v=0.5,
        degrees=0.0,
        translate=0.15,
        scale=0.6,
        shear=0.0,
        perspective=0.0,
        flipud=0.2,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
        copy_paste=0.1,
        
        workers=8,
        amp=True,
        close_mosaic=20,
        freeze=0,
        
        deterministic=False,
        verbose=True,
        val=True,
        split='val',
    )
    
    print("\n✓ 训练完成!")
    print(f"最佳模型: {results.save_dir / 'weights' / 'best.pt'}")
    
    save_training_info(results, data_yaml, epochs, batch, imgsz)
    
    return results


def save_training_info(results, data_yaml, epochs, batch, imgsz):
    info = {
        'timestamp': datetime.now().isoformat(),
        'data_yaml': str(data_yaml),
        'epochs': epochs,
        'batch': batch,
        'imgsz': imgsz,
        'save_dir': str(results.save_dir),
        'best_model': str(results.save_dir / 'weights' / 'best.pt'),
    }
    
    with open(results.save_dir / 'training_info.json', 'w') as f:
        json.dump(info, f, indent=2)
    
    print(f"训练信息已保存: {results.save_dir / 'training_info.json'}")


def validate_model(model_path: str, data_yaml: str):
    print("\n验证模型...")
    model = YOLO(model_path)
    
    metrics = model.val(data=data_yaml)
    
    print(f"\n验证结果:")
    print(f"  mAP50: {metrics.box.map50:.4f}")
    print(f"  mAP50-95: {metrics.box.map:.4f}")
    print(f"  Precision: {metrics.box.mp:.4f}")
    print(f"  Recall: {metrics.box.mr:.4f}")
    
    return metrics


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='训练 YOLOv8 怪物检测模型 - 双卡 3090')
    parser.add_argument('--data', type=str, default='./dataset/data.yaml', 
                        help='数据集配置文件路径')
    parser.add_argument('--epochs', type=int, default=300, help='训练轮数')
    parser.add_argument('--batch', type=int, default=32, help='单卡 batch size')
    parser.add_argument('--imgsz', type=int, default=640, help='图像尺寸')
    parser.add_argument('--resume', type=str, default=None, 
                        help='从检查点恢复训练 (路径到 last.pt)')
    parser.add_argument('--validate', action='store_true', 
                        help='训练完成后验证模型')
    
    args = parser.parse_args()
    
    results = train(
        data_yaml=args.data,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        resume=args.resume,
    )
    
    if args.validate:
        best_model = results.save_dir / 'weights' / 'best.pt'
        validate_model(str(best_model), args.data)
