"""
云端训练脚本 - Kaggle/Colab/恒源云
支持数据生成和训练一体化
使用 YOLOv8s 模型
"""

import os
import sys
import torch
from pathlib import Path
from ultralytics import YOLO
import argparse


def generate_dataset(mob_dir: str, bg_dir: str, output_dir: str, num_samples: int = 5000):
    """生成训练数据集"""
    print("=" * 60)
    print("步骤 1: 生成训练数据集")
    print("=" * 60)
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from generate_data import HighQualityDataGenerator
    
    generator = HighQualityDataGenerator(mob_dir, bg_dir, output_dir)
    
    generator.generate_dataset(
        total_samples=num_samples,
        train_ratio=0.85,
        num_mobs_range=(5, 20),
        scale_range=(0.06, 0.5)
    )
    
    return output_dir


def train(data_yaml: str, epochs: int = 100, batch: int = 16, imgsz: int = 640,
          project: str = './runs', name: str = 'mob_detector_yolov8s'):
    """训练 YOLOv8s 模型"""
    print("\n" + "=" * 60)
    print("步骤 2: 训练 YOLOv8s 模型")
    print("=" * 60)
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"使用设备: {device}")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    
    data_path = Path(data_yaml)
    if not data_path.exists():
        raise FileNotFoundError(f"数据集配置文件不存在: {data_path}")
    
    print(f"\n数据集配置: {data_path}")
    print(f"训练参数: epochs={epochs}, batch={batch}, imgsz={imgsz}")
    
    model = YOLO('yolov8s.pt')
    
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
    
    return results


def validate_model(model_path: str, data_yaml: str):
    """验证模型"""
    print("\n" + "=" * 60)
    print("步骤 3: 验证模型")
    print("=" * 60)
    
    model = YOLO(model_path)
    metrics = model.val(data=data_yaml)
    
    print(f"\n验证结果:")
    print(f"  mAP50: {metrics.box.map50:.4f}")
    print(f"  mAP50-95: {metrics.box.map:.4f}")
    print(f"  Precision: {metrics.box.mp:.4f}")
    print(f"  Recall: {metrics.box.mr:.4f}")
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description='云端训练 YOLOv8s 怪物检测模型')
    parser.add_argument('--mode', type=str, default='all', 
                        choices=['generate', 'train', 'validate', 'all'],
                        help='运行模式: generate(仅生成数据), train(仅训练), validate(仅验证), all(完整流程)')
    parser.add_argument('--mob-dir', type=str, default='./mob_images',
                        help='Mob 图像目录')
    parser.add_argument('--bg-dir', type=str, default='./backgrounds',
                        help='背景图像目录')
    parser.add_argument('--dataset-dir', type=str, default='./dataset',
                        help='数据集输出目录')
    parser.add_argument('--num-samples', type=int, default=5000,
                        help='生成样本数量 (Kaggle/Colab推荐5000, 恒源云推荐10000)')
    parser.add_argument('--data-yaml', type=str, default=None,
                        help='数据集配置文件路径 (如果已存在)')
    parser.add_argument('--epochs', type=int, default=100,
                        help='训练轮数')
    parser.add_argument('--batch', type=int, default=16,
                        help='Batch size (Kaggle/Colab推荐16, 恒源云推荐32)')
    parser.add_argument('--imgsz', type=int, default=640,
                        help='图像尺寸')
    parser.add_argument('--project', type=str, default='./runs',
                        help='项目保存路径')
    parser.add_argument('--name', type=str, default='mob_detector_yolov8s',
                        help='实验名称')
    parser.add_argument('--model', type=str, default=None,
                        help='验证模型路径')
    
    args = parser.parse_args()
    
    if args.mode in ['generate', 'all']:
        if args.data_yaml is None:
            generate_dataset(
                mob_dir=args.mob_dir,
                bg_dir=args.bg_dir,
                output_dir=args.dataset_dir,
                num_samples=args.num_samples
            )
            data_yaml = str(Path(args.dataset_dir) / 'data.yaml')
        else:
            data_yaml = args.data_yaml
            print(f"\n使用现有数据集: {data_yaml}")
    else:
        if args.data_yaml is None:
            data_yaml = str(Path(args.dataset_dir) / 'data.yaml')
        else:
            data_yaml = args.data_yaml
    
    if args.mode in ['train', 'all']:
        results = train(
            data_yaml=data_yaml,
            epochs=args.epochs,
            batch=args.batch,
            imgsz=args.imgsz,
            project=args.project,
            name=args.name
        )
        best_model = str(Path(results.save_dir) / 'weights' / 'best.pt')
    else:
        best_model = args.model
    
    if args.mode in ['validate', 'all']:
        if best_model is None:
            raise ValueError("请提供模型路径进行验证 (--model)")
        validate_model(best_model, data_yaml)
    
    print("\n" + "=" * 60)
    print("✓ 所有步骤完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
