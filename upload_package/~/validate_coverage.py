"""
验证 mob 覆盖情况
检查训练数据生成是否覆盖所有 mob 类型
"""

import cv2
import numpy as np
from pathlib import Path
from collections import defaultdict
import json


def check_mob_images_coverage(mob_dir: str):
    mob_path = Path(mob_dir)
    
    mob_files = {}
    for f in mob_path.glob("*.png"):
        if not f.name.endswith('.disable'):
            mob_files[f.stem] = f
    
    print(f"Mob 图像目录: {mob_dir}")
    print(f"找到 {len(mob_files)} 种 mob 图像")
    
    return mob_files


def check_dataset_coverage(dataset_dir: str, mob_files: dict):
    dataset_path = Path(dataset_dir)
    labels_dir = dataset_path / 'labels'
    
    if not labels_dir.exists():
        print(f"数据集标签目录不存在: {labels_dir}")
        return
    
    class_usage = defaultdict(int)
    total_labels = 0
    
    for split in ['train', 'val']:
        split_dir = labels_dir / split
        if not split_dir.exists():
            continue
            
        for label_file in split_dir.glob("*.txt"):
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        class_id = int(parts[0])
                        class_usage[class_id] += 1
                        total_labels += 1
    
    classes_file = dataset_path / 'classes.txt'
    if classes_file.exists():
        with open(classes_file, 'r') as f:
            classes = [line.strip() for line in f if line.strip()]
    else:
        classes = [f"class_{i}" for i in range(max(class_usage.keys()) + 1)]
    
    print(f"\n数据集覆盖分析:")
    print(f"  总标签数: {total_labels}")
    print(f"  使用的类别数: {len(class_usage)}")
    
    missing_classes = []
    for i, class_name in enumerate(classes):
        if i not in class_usage:
            missing_classes.append(class_name)
    
    if missing_classes:
        print(f"\n⚠ 未使用的 mob ({len(missing_classes)}):")
        for name in missing_classes:
            print(f"    - {name}")
    else:
        print(f"\n✓ 所有 {len(classes)} 种 mob 都已覆盖!")
    
    print(f"\n各类别使用统计:")
    usage_list = [(classes[i], count) for i, count in class_usage.items()]
    usage_list.sort(key=lambda x: x[1], reverse=True)
    
    print("  最多的 10 个:")
    for name, count in usage_list[:10]:
        print(f"    {name}: {count}")
    
    print("  最少的 10 个:")
    for name, count in usage_list[-10:]:
        print(f"    {name}: {count}")
    
    return {
        'total_labels': total_labels,
        'classes_used': len(class_usage),
        'missing_classes': missing_classes,
        'usage_stats': dict(usage_list)
    }


def check_training_samples(dataset_dir: str):
    dataset_path = Path(dataset_dir)
    images_dir = dataset_path / 'images'
    
    train_count = 0
    val_count = 0
    
    train_dir = images_dir / 'train'
    if train_dir.exists():
        train_count = len(list(train_dir.glob("*.png")))
    
    val_dir = images_dir / 'val'
    if val_dir.exists():
        val_count = len(list(val_dir.glob("*.png")))
    
    print(f"\n训练样本统计:")
    print(f"  训练集: {train_count} 张")
    print(f"  验证集: {val_count} 张")
    print(f"  总计: {train_count + val_count} 张")
    
    return {'train': train_count, 'val': val_count}


def main():
    print("=" * 60)
    print("Mob 覆盖验证工具")
    print("=" * 60)
    
    mob_dir = "./mob_images"
    dataset_dir = "./dataset"
    
    mob_files = check_mob_images_coverage(mob_dir)
    
    coverage = check_dataset_coverage(dataset_dir, mob_files)
    
    samples = check_training_samples(dataset_dir)
    
    print("\n" + "=" * 60)
    print("验证完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
