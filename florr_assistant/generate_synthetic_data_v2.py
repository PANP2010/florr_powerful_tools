"""
合成训练数据生成器 - 使用真实游戏背景
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
    
    MAP_MOBS = {
        'g': ['ladybug', 'bee', 'beetle', 'ant_baby', 'ant_worker', 'ant_soldier', 
              'centipede', 'fly', 'bumble_bee', 'hornet', 'mantis', 'spider'],
        'ah': ['ant_baby', 'ant_worker', 'ant_soldier', 'ant_queen', 'ant_egg', 
               'ant_hole', 'fire_ant_baby', 'fire_ant_worker', 'fire_ant_soldier'],
        'd': ['beetle_mummy', 'beetle_pharaoh', 'beetle_nazar', 'scorpion', 
              'centipede_desert', 'sandstorm', 'digger', 'firefly', 'firefly_magic'],
        'f': ['centipede', 'centipede_body', 'mantis', 'leafbug', 'leafbug_shiny',
              'spider', 'hornet', 'wasp', 'beetle'],
        'h': ['beetle_hel', 'centipede_hel', 'centipede_hel_body', 'spider_hel',
              'wasp_hel', 'leech', 'leech_body', 'moth'],
        'o': ['jellyfish', 'bubble', 'crab', 'crab_mecha', 'starfish', 
              'sponge', 'shell', 'worm'],
        's': ['roach', 'fly', 'centipede', 'spider', 'beetle', 'worm', 'worm_guts']
    }
    
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
                if len(img.shape) == 3 and img.shape[2] == 4:
                    self.mob_images[mob_name] = img
                elif len(img.shape) == 3:
                    alpha = np.ones((img.shape[0], img.shape[1], 1), dtype=img.dtype) * 255
                    self.mob_images[mob_name] = np.concatenate([img, alpha], axis=2)
        
        self.mob_classes = {name: idx for idx, name in enumerate(sorted(self.mob_images.keys()))}
        
        with open(self.output_dir / 'classes.txt', 'w') as f:
            for name, idx in sorted(self.mob_classes.items(), key=lambda x: x[1]):
                f.write(f"{name}\n")
        
        print(f"加载了 {len(self.mob_images)} 种怪物图像")
    
    def _load_backgrounds(self):
        print(f"加载背景图像: {self.background_images_dir}")
        
        for bg_path in sorted(self.background_images_dir.glob("*.png")):
            img = cv2.imread(str(bg_path))
            if img is not None:
                name = bg_path.stem
                map_type = name[0] if name[0] in self.MAP_MOBS else 'g'
                self.backgrounds.append({
                    'image': img,
                    'name': name,
                    'map_type': map_type
                })
        
        print(f"加载了 {len(self.backgrounds)} 张背景图像")
        
        map_counts = {}
        for bg in self.backgrounds:
            mt = bg['map_type']
            map_counts[mt] = map_counts.get(mt, 0) + 1
        for mt, count in sorted(map_counts.items()):
            print(f"  {mt}: {count} 张")
    
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
                        background: Dict,
                        num_mobs_range: Tuple[int, int] = (3, 15),
                        scale_range: Tuple[float, float] = (0.3, 1.5)) -> Tuple[np.ndarray, List[Dict]]:
        
        bg_image = background['image'].copy()
        map_type = background['map_type']
        bg_h, bg_w = bg_image.shape[:2]
        
        available_mobs = self.MAP_MOBS.get(map_type, list(self.mob_images.keys()))
        available_mobs = [m for m in available_mobs if m in self.mob_images]
        
        if not available_mobs:
            available_mobs = list(self.mob_images.keys())
        
        num_mobs = random.randint(num_mobs_range[0], num_mobs_range[1])
        
        annotations = []
        occupied_regions = []
        
        for _ in range(num_mobs):
            mob_name = random.choice(available_mobs)
            mob_img = self.mob_images[mob_name].copy()
            
            scale = random.uniform(scale_range[0], scale_range[1])
            mob_img = cv2.resize(mob_img, None, fx=scale, fy=scale,
                                interpolation=cv2.INTER_CUBIC)
            
            mob_h, mob_w = mob_img.shape[:2]
            
            max_attempts = 20
            placed = False
            
            for _ in range(max_attempts):
                max_x = max(0, bg_w - mob_w)
                max_y = max(0, bg_h - mob_h)
                
                x = random.randint(0, max_x) if max_x > 0 else 0
                y = random.randint(0, max_y) if max_y > 0 else 0
                
                overlap = False
                for region in occupied_regions:
                    if self._check_overlap((x, y, x + mob_w, y + mob_h), region):
                        overlap = True
                        break
                
                if not overlap:
                    bg_image = self._overlay_image(bg_image, mob_img, x, y, 1.0)
                    occupied_regions.append((x, y, x + mob_w, y + mob_h))
                    placed = True
                    break
            
            if placed:
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
        
        return bg_image, annotations
    
    def _check_overlap(self, box1, box2, threshold=0.3):
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        iou = inter / (area1 + area2 - inter) if (area1 + area2 - inter) > 0 else 0
        
        return iou > threshold
    
    def generate_dataset(self, 
                         samples_per_bg: int = 50,
                         train_ratio: float = 0.8,
                         num_mobs_range: Tuple[int, int] = (3, 15),
                         scale_range: Tuple[float, float] = (0.3, 1.5)):
        
        train_images_dir = self.output_dir / 'images' / 'train'
        train_labels_dir = self.output_dir / 'labels' / 'train'
        val_images_dir = self.output_dir / 'images' / 'val'
        val_labels_dir = self.output_dir / 'labels' / 'val'
        
        for d in [train_images_dir, train_labels_dir, val_images_dir, val_labels_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        total_samples = len(self.backgrounds) * samples_per_bg
        print(f"\n生成 {total_samples} 个合成样本...")
        
        sample_idx = 0
        train_count = 0
        val_count = 0
        
        for bg_idx, bg in enumerate(self.backgrounds):
            for i in range(samples_per_bg):
                try:
                    image, annotations = self.generate_sample(
                        bg, num_mobs_range, scale_range
                    )
                    
                    is_train = sample_idx < int(total_samples * train_ratio)
                    
                    if is_train:
                        image_dir = train_images_dir
                        label_dir = train_labels_dir
                        train_count += 1
                    else:
                        image_dir = val_images_dir
                        label_dir = val_labels_dir
                        val_count += 1
                    
                    image_name = f"synthetic_{sample_idx:06d}"
                    
                    cv2.imwrite(str(image_dir / f"{image_name}.png"), image)
                    
                    with open(label_dir / f"{image_name}.txt", 'w') as f:
                        for ann in annotations:
                            f.write(f"{ann['class_id']} {ann['bbox'][0]:.6f} {ann['bbox'][1]:.6f} {ann['bbox'][2]:.6f} {ann['bbox'][3]:.6f}\n")
                    
                    sample_idx += 1
                    
                    if sample_idx % 100 == 0:
                        print(f"  已生成 {sample_idx}/{total_samples} 个样本")
                        
                except Exception as e:
                    print(f"  生成样本 {sample_idx} 失败: {e}")
        
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
        print(f"  训练集: {train_count} 张图片")
        print(f"  验证集: {val_count} 张图片")
        print(f"  配置文件: {self.output_dir / 'data.yaml'}")


def main():
    print("=" * 60)
    print("合成训练数据生成器 - 真实游戏背景")
    print("=" * 60)
    
    mob_dir = "/Users/panjiyang/Documents/trae_projects/florr_ai/image/0_no-background/mob/common"
    bg_dir = "/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data"
    output_dir = "/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/synthetic_mobs_v2"
    
    generator = SyntheticDataGenerator(mob_dir, bg_dir, output_dir)
    
    generator.generate_dataset(
        samples_per_bg=30,
        train_ratio=0.8,
        num_mobs_range=(3, 12),
        scale_range=(0.4, 1.2)
    )


if __name__ == '__main__':
    main()
