"""
训练YOLO怪物检测模型 V3
使用合成数据集训练（支持旋转/缩放/聚集）
"""

from ultralytics import YOLO
from pathlib import Path


def train_yolo():
    print("=" * 60)
    print("训练YOLO怪物检测模型 V3")
    print("=" * 60)
    
    data_yaml = Path("/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/synthetic_mobs_v3/data.yaml")
    
    print(f"\n数据集配置: {data_yaml}")
    
    model = YOLO('yolov8n.pt')
    
    print("\n开始训练...")
    results = model.train(
        data=str(data_yaml),
        epochs=100,
        imgsz=640,
        batch=16,
        name='mob_detector_v3',
        project='/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/runs',
        device='cpu',
        patience=15,
        save=True,
        plots=True,
        augment=True,
        degrees=0,
        scale=0,
        flipud=0.5,
        fliplr=0.5
    )
    
    print("\n✓ 训练完成!")
    print(f"最佳模型: {results.save_dir / 'weights' / 'best.pt'}")
    
    return results


if __name__ == '__main__':
    train_yolo()
