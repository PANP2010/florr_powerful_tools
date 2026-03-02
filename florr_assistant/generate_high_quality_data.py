"""
高质量训练数据生成器 V4
- 更多数据量 (每张背景60张)
- 更小怪物尺寸 (0.08-0.5)
- 更多旋转和变换
- 更密集的怪物分布
"""

import cv2
import numpy as np
import random
from pathlib import Path
from typing import List, Dict, Tuple
import math


class HighQualityDataGenerator:
    
    MAP_MOBS = {
        'g': ['ladybug', 'bee', 'beetle', 'ant_baby', 'ant_worker', 'ant_soldier', 
              'centipede', 'fly', 'bumble_bee', 'hornet', 'mantis', 'spider',
              'rock', 'ladybug_dark', 'ladybug_shiny'],
        'ah': ['ant_baby', 'ant_worker', 'ant_soldier', 'ant_queen', 'ant_egg', 
               'ant_hole', 'fire_ant_baby', 'fire_ant_worker', 'fire_ant_soldier',
               'fire_ant_burrow', 'fire_ant_egg', 'fire_ant_queen',
               'termite_baby', 'termite_egg', 'termite_mound', 'termite_overmind', 
               'termite_soldier', 'termite_worker'],
        'd': ['beetle_mummy', 'beetle_pharaoh', 'beetle_nazar', 'scorpion', 
              'centipede_desert', 'sandstorm', 'digger', 'firefly', 'firefly_magic',
              'tomb', 'trader', 'cactus'],
        'f': ['centipede', 'centipede_body', 'mantis', 'leafbug', 'leafbug_shiny',
              'spider', 'hornet', 'wasp', 'beetle', 'dummy', 'centipede_evil', 'bush'],
        'h': ['beetle_hel', 'centipede_hel', 'centipede_hel_body', 'spider_hel',
              'wasp_hel', 'leech', 'leech_body', 'moth', 'gambler', 'gambler_old'],
        'o': ['jellyfish', 'bubble', 'crab', 'crab_mecha', 'starfish', 
              'sponge', 'shell', 'worm'],
        's': ['roach', 'fly', 'centipede', 'spider', 'beetle', 'worm', 'worm_guts'],
        'fc': ['mecha_flower', 'mecha_flower_old', 'spider_mecha', 'wasp_mecha', 'crab_mecha'],
    }
    
    ALL_MAPS_MOBS = ['assembler', 'barrel', 'dandelion', 'oracle', 'titan', 'square']
    
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
                if name.startswith('fc'):
                    map_type = 'fc'
                elif name.startswith('ah'):
                    map_type = 'ah'
                else:
                    map_type = name[0] if name[0] in self.MAP_MOBS else 'g'
                self.backgrounds.append({
                    'image': img,
                    'name': name,
                    'map_type': map_type
                })
        
        print(f"加载了 {len(self.backgrounds)} 张背景图像")
    
    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        cos = np.abs(rotation_matrix[0, 0])
        sin = np.abs(rotation_matrix[0, 1])
        
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        
        rotation_matrix[0, 2] += (new_w / 2) - center[0]
        rotation_matrix[1, 2] += (new_h / 2) - center[1]
        
        rotated = cv2.warpAffine(
            image, 
            rotation_matrix, 
            (new_w, new_h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0, 0)
        )
        
        return rotated
    
    def _adjust_brightness(self, image: np.ndarray, factor: float) -> np.ndarray:
        hsv = cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = hsv[:, :, 2] * factor
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
        bgr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        result = image.copy()
        result[:, :, :3] = bgr
        return result
    
    def _overlay_image(self, background: np.ndarray, overlay: np.ndarray, 
                       x: int, y: int) -> Tuple[np.ndarray, int, int, int, int]:
        h, w = overlay.shape[:2]
        
        bg_h, bg_w = background.shape[:2]
        
        src_x = 0
        src_y = 0
        dst_x = x
        dst_y = y
        copy_w = w
        copy_h = h
        
        if x < 0:
            src_x = -x
            dst_x = 0
            copy_w += x
        if y < 0:
            src_y = -y
            dst_y = 0
            copy_h += y
        if x + w > bg_w:
            copy_w = bg_w - x
        if y + h > bg_h:
            copy_h = bg_h - y
        
        if copy_w <= 0 or copy_h <= 0:
            return background, x, y, w, h
        
        overlay_roi = overlay[src_y:src_y+copy_h, src_x:src_x+copy_w]
        bg_roi = background[dst_y:dst_y+copy_h, dst_x:dst_x+copy_w]
        
        overlay_rgb = overlay_roi[:, :, :3]
        overlay_alpha = overlay_roi[:, :, 3:] / 255.0
        
        blended = bg_roi * (1 - overlay_alpha) + overlay_rgb * overlay_alpha
        background[dst_y:dst_y+copy_h, dst_x:dst_x+copy_w] = blended.astype(np.uint8)
        
        actual_x = max(0, x)
        actual_y = max(0, y)
        actual_w = min(w, bg_w - actual_x)
        actual_h = min(h, bg_h - actual_y)
        
        return background, actual_x, actual_y, actual_w, actual_h
    
    def generate_sample(self, 
                        background: Dict,
                        num_mobs_range: Tuple[int, int] = (5, 20),
                        scale_range: Tuple[float, float] = (0.08, 0.5)) -> Tuple[np.ndarray, List[Dict]]:
        
        bg_image = background['image'].copy()
        map_type = background['map_type']
        bg_h, bg_w = bg_image.shape[:2]
        
        available_mobs = self.MAP_MOBS.get(map_type, list(self.mob_images.keys()))
        available_mobs = [m for m in available_mobs if m in self.mob_images]
        
        all_maps_mobs = [m for m in self.ALL_MAPS_MOBS if m in self.mob_images]
        
        if not available_mobs:
            available_mobs = list(self.mob_images.keys())
        
        num_mobs = random.randint(num_mobs_range[0], num_mobs_range[1])
        
        if random.random() < 0.4:
            num_mobs = random.randint(int(num_mobs_range[1] * 0.7), num_mobs_range[1])
        
        annotations = []
        placed_boxes = []
        
        for i in range(num_mobs):
            if random.random() < 0.15 and all_maps_mobs:
                mob_name = random.choice(all_maps_mobs)
            else:
                mob_name = random.choice(available_mobs)
            mob_img = self.mob_images[mob_name].copy()
            
            scale = random.uniform(scale_range[0], scale_range[1])
            
            if random.random() < 0.4:
                scale = random.uniform(scale_range[0], scale_range[0] + 0.15)
            elif random.random() < 0.2:
                scale = random.uniform(scale_range[1] - 0.15, scale_range[1])
            
            mob_img = cv2.resize(mob_img, None, fx=scale, fy=scale,
                                interpolation=cv2.INTER_CUBIC)
            
            angle = random.uniform(0, 360)
            mob_img = self._rotate_image(mob_img, angle)
            
            if random.random() < 0.3:
                brightness_factor = random.uniform(0.7, 1.3)
                mob_img = self._adjust_brightness(mob_img, brightness_factor)
            
            mob_h, mob_w = mob_img.shape[:2]
            
            max_x = bg_w - mob_w
            max_y = bg_h - mob_h
            
            placed = False
            attempts = 0
            max_attempts = 10
            
            while attempts < max_attempts and not placed:
                if max_x > 0:
                    x = random.randint(0, max_x)
                else:
                    x = 0
                
                if max_y > 0:
                    y = random.randint(0, max_y)
                else:
                    y = 0
                
                placed = True
                
                attempts += 1
            
            if placed:
                bg_image, actual_x, actual_y, actual_w, actual_h = self._overlay_image(
                    bg_image, mob_img, x, y
                )
                
                placed_boxes.append((actual_x, actual_y, actual_x + actual_w, actual_y + actual_h))
                
                class_id = self.mob_classes[mob_name]
                
                x_center = (actual_x + actual_w / 2) / bg_w
                y_center = (actual_y + actual_h / 2) / bg_h
                width = actual_w / bg_w
                height = actual_h / bg_h
                
                annotations.append({
                    'class_id': class_id,
                    'class_name': mob_name,
                    'bbox': [x_center, y_center, width, height],
                    'bbox_abs': [actual_x, actual_y, actual_x + actual_w, actual_y + actual_h],
                    'scale': scale,
                    'angle': angle
                })
        
        return bg_image, annotations
    
    def generate_dataset(self, 
                         samples_per_bg: int = 60,
                         train_ratio: float = 0.8,
                         num_mobs_range: Tuple[int, int] = (5, 20),
                         scale_range: Tuple[float, float] = (0.08, 0.5)):
        
        train_images_dir = self.output_dir / 'images' / 'train'
        train_labels_dir = self.output_dir / 'labels' / 'train'
        val_images_dir = self.output_dir / 'images' / 'val'
        val_labels_dir = self.output_dir / 'labels' / 'val'
        
        for d in [train_images_dir, train_labels_dir, val_images_dir, val_labels_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        total_samples = len(self.backgrounds) * samples_per_bg
        print(f"\n生成 {total_samples} 个高质量合成样本...")
        print(f"  缩放范围: {scale_range[0]:.2f} - {scale_range[1]:.2f}")
        print(f"  怪物数量: {num_mobs_range[0]} - {num_mobs_range[1]}")
        print(f"  支持旋转: 0-360度")
        print(f"  亮度调整: 30%概率")
        
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
                    
                    image_name = f"hq_{sample_idx:06d}"
                    
                    cv2.imwrite(str(image_dir / f"{image_name}.png"), image)
                    
                    with open(label_dir / f"{image_name}.txt", 'w') as f:
                        for ann in annotations:
                            f.write(f"{ann['class_id']} {ann['bbox'][0]:.6f} {ann['bbox'][1]:.6f} {ann['bbox'][2]:.6f} {ann['bbox'][3]:.6f}\n")
                    
                    sample_idx += 1
                    
                    if sample_idx % 200 == 0:
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
        
        print(f"\n✓ 高质量数据集生成完成!")
        print(f"  训练集: {train_count} 张图片")
        print(f"  验证集: {val_count} 张图片")
        print(f"  配置文件: {self.output_dir / 'data.yaml'}")


def main():
    print("=" * 60)
    print("高质量训练数据生成器 V4")
    print("=" * 60)
    
    mob_dir = "/Users/panjiyang/Documents/trae_projects/florr_ai/image/0_no-background/mob/common"
    bg_dir = "/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data"
    output_dir = "/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/data/synthetic_mobs_v4"
    
    generator = HighQualityDataGenerator(mob_dir, bg_dir, output_dir)
    
    generator.generate_dataset(
        samples_per_bg=60,
        train_ratio=0.85,
        num_mobs_range=(5, 20),
        scale_range=(0.08, 0.5)
    )


if __name__ == '__main__':
    main()
