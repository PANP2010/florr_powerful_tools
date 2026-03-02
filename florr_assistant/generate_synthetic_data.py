"""
合成训练数据生成器
将无背景怪物图像叠加到游戏截图上，自动生成YOLO训练数据
"""

import cv2
import numpy as np
import json
import random
from pathlib import Path
from typing import List, Dict, Tuple
import os


class SyntheticDataGenerator:
    def __init__(self, 
                 mob_images_dir: str,
                 background_images_dir: str,
                 output_dir: str):
        self.mob_images_dir = Path(mob_images_dir)
        self.background_images_dir = Path(background_images_dir)
        self.output_dir = Path(output_dir)
        
        self.mob_images = {}
        self.backgrounds = []
        self.mob_classes = {}
        
        self._load_mob_images()
        self._load_backgrounds()
    
    def _load_mob_images(self):
        print(f"加载怪物图像: {self.mob_images_dir}")
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        for mob_path in self.mob_images_dir.glob("*.png"):
            if mob_path.name.endswith('.disable'):
                continue
            
            mob_name = mob_path.stem
            img = cv2.imread(str(mob_path), cv2.IMREAD_UNCHANGED)
            
            if img is not None:
                if img.shape[2] == 4:
                    self.mob_images[mob_name] = img
                else:
                    alpha = np.ones((img.shape[0], img.shape[1], 1), dtype=img.dtype) * 255
                    self.mob_images[mob_name] = np.concatenate([img, alpha], axis=2)
        
        self.mob_classes = {name: idx for idx, name in enumerate(sorted(self.mob_images.keys()))}
        
        with open(self.output_dir / 'classes.txt', 'w') as f:
            for name, idx in sorted(self.mob_classes.items(), key=lambda x: x[1]):
                f.write(f"{name}\n")
        
        print(f"加载了 {len(self.mob_images)} 种怪物图像")
        print(f"类别保存到: {self.output_dir / 'classes.txt'}")
    
    def _load_backgrounds(self):
        print(f"加载背景图像: {self.background_images_dir}")
        
        for bg_path in self.background_images_dir.glob("*.png"):
            img = cv2.imread(str(bg_path))
            if img is not None:
                self.backgrounds.append(img)
        
        for bg_path in self.background_images_dir.glob("*.jpg"):
            img = cv2.imread(str(bg_path))
            if img is not None:
                self.backgrounds.append(img)
        
        print(f"加载了 {len(self.backgrounds)} 张背景图像")
    
    def _overlay_image(self, background: np.ndarray, overlay: np.ndarray, 
                       x: int, y: int, scale: float = 1.0) -> np.ndarray:
        if scale != 1.0:
            overlay = cv2.resize(overlay, None, fx=scale, fy=scale, 
                                interpolation=cv2.INTER_CUBIC)
        
        h, w = overlay.shape[:2]
        
        if x < 0: x = 0
        if y < 0: y = 0
        if x + w > background.shape[1]: x = background.shape[1] - w
        if y + h > background.shape[0]: y = background.shape[0] - h
        
        if x < 0 or y < 0:
            return background
        
        overlay_rgb = overlay[:, :, :3]
        overlay_alpha = overlay[:, :, 3:] / 255.0
        
        roi = background[y:y+h, x:x+w]
        
        blended = roi * (1 - overlay_alpha) + overlay_rgb * overlay_alpha
        background[y:y+h, x:x+w] = blended.astype(np.uint8)
        
        return background
    
    def generate_sample(self, 
                        num_mobs: Tuple[int, int] = (1, 10),
                        scale_range: Tuple[float, float] = (0.5, 2.0)) -> Tuple[np.ndarray, List[Dict]]:
        if not self.backgrounds:
            raise ValueError("没有背景图像")
        
        background = self.backgrounds[random.randint(0, len(self.backgrounds) - 1)].copy()
        bg_h, bg_w = background.shape[:2]
        
        num_mobs_to_add = random.randint(num_mobs[0], num_mobs[1])
        
        annotations = []
        
        for _ in range(num_mobs_to_add):
            mob_name = random.choice(list(self.mob_images.keys()))
            mob_img = self.mob_images[mob_name].copy()
            
            scale = random.uniform(scale_range[0], scale_range[1])
            mob_img = cv2.resize(mob_img, None, fx=scale, fy=scale,
                                interpolation=cv2.INTER_CUBIC)
            
            mob_h, mob_w = mob_img.shape[:2]
            
            max_x = max(0, bg_w - mob_w)
            max_y = max(0, bg_h - mob_h)
            
            x = random.randint(0, max_x) if max_x > 0 else 0
            y = random.randint(0, max_y) if max_y > 0 else 0
            
            background = self._overlay_image(background, mob_img, x, y, 1.0)
            
            class_id = self.mob_classes[mob_name]
            
            x_center = (x + mob_w / 2) / bg_w
            y_center = (y + mob_h / 2) / bg_h
            width = mob_w / bg_w
            height = mob_h / bg_h
            
            annotations.append({
                'class_id': class_id,
                'class_name': mob_name,
                'bbox': [x_center, y_center, width, height],
                'bbox_abs': [x, y, x + mob_w, y + mob_h]
            })
        
        return background, annotations
    
    def generate_dataset(self, 
                         num_samples: int = 1000,
                         train_ratio: float = 0.8,
                         num_mobs: Tuple[int, int] = (1, 10),
                         scale_range: Tuple[float, float] = (0.5, 2.0)):
        
        train_images_dir = self.output_dir / 'images' / 'train'
        train_labels_dir = self.output_dir / 'labels' / 'train'
        val_images_dir = self.output_dir / 'images' / 'val'
        val_labels_dir = self.output_dir / 'labels' / 'val'
        
        for d in [train_images_dir, train_labels_dir, val_images_dir, val_labels_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        print(f"\n生成 {num_samples} 个合成样本...")
        
        for i in range(num_samples):
            try:
                image, annotations = self.generate_sample(num_mobs, scale_range)
                
                is_train = i < int(num_samples * train_ratio)
                
                if is_train:
                    image_dir = train_images_dir
                    label_dir = train_labels_dir
                else:
                    image_dir = val_images_dir
                    label_dir = val_labels_dir
                
                image_name = f"synthetic_{i:06d}"
                
                cv2.imwrite(str(image_dir / f"{image_name}.png"), image)
                
                with open(label_dir / f"{image_name}.txt", 'w') as f:
                    for ann in annotations:
                        f.write(f"{ann['class_id']} {ann['bbox'][0]:.6f} {ann['bbox'][1]:.6f} {ann['bbox'][2]:.6f} {ann['bbox'][3]:.6f}\n")
                
                if (i + 1) % 100 == 0:
                    print(f"  已生成 {i + 1}/{num_samples} 个样本")
                    
            except Exception as e:
                print(f"  生成样本 {i} 失败: {e}")
        
        data_yaml = f"""path: {self.output_dir.absolute()}
train: images/train
val: images/val

nc: {len(self.mob_classes)}
names:
"""
        for name, idx in sorted(self.mob_classes.items(), key=lambda x: x[1]):
            data_yaml += f"  {idx}: {name}\n"
        
        with open(self.output_dir / 'data.yaml', 'w') as f:
            f.write(data_yaml)
        
        print(f"\n✓ 数据集生成完成!")
        print(f"  训练集: {len(list(train_images_dir.glob('*.png')))} 张图片")
        print(f"  验证集: {len(list(val_images_dir.glob('*.png')))} 张图片")
        print(f"  配置文件: {self.output_dir / 'data.yaml'}")


def main():
    print("=" * 60)
    print("合成训练数据生成器")
    print("=" * 60)
    
    mob_dir = "/Users/panjiyang/Documents/trae_projects/florr_ai/image/0_no-background/mob/common"
    bg_dir = "/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/florr-auto-pathing/map_dataset"
    output_dir = "/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/synthetic_mobs"
    
    generator = SyntheticDataGenerator(mob_dir, bg_dir, output_dir)
    
    generator.generate_dataset(
        num_samples=1000,
        train_ratio=0.8,
        num_mobs=(1, 15),
        scale_range=(0.3, 1.5)
    )


if __name__ == '__main__':
    main()
