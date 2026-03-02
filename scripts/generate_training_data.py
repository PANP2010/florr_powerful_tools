from PIL import Image
import os
import random

def generate_map_images(map_file, map_name, num_images=64, target_size=300):
    if not os.path.exists(map_file):
        print(f"文件不存在: {map_file}")
        return 0
    
    if map_name == "worm's inside":
        map_dir = f"./florr-auto-pathing/map_dataset/classification/images/train/worm's inside"
    else:
        map_dir = f"./florr-auto-pathing/map_dataset/classification/images/train/{map_name}"
    
    os.makedirs(map_dir, exist_ok=True)
    print(f"创建目录: {map_dir}")
    
    img = Image.open(map_file)
    
    if img.mode == 'RGBA':
        img_rgb = img.convert('RGB')
    else:
        img_rgb = img
    
    img_resized = img_rgb.resize((target_size, target_size), Image.LANCZOS)
    
    created_count = 0
    for i in range(num_images):
        try:
            output_path = os.path.join(map_dir, f"{map_name}_{i}.jpg")
            
            if i == 0:
                img_resized.save(output_path)
            else:
                angle = random.uniform(-10, 10)
                brightness = random.uniform(0.9, 1.1)
                contrast = random.uniform(0.9, 1.1)
                
                rotated = img_resized.rotate(angle, resample=Image.BILINEAR)
                
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Brightness(rotated)
                brightened = enhancer.enhance(brightness)
                
                enhancer = ImageEnhance.Contrast(brightened)
                final = enhancer.enhance(contrast)
                
                final.save(output_path)
            
            created_count += 1
        except Exception as e:
            print(f"错误: {map_name}_{i}: {e}")
    
    return created_count

maps = [
    ('factory.png', 'factory'),
    ('garden.png', 'garden'),
    ('sewers.png', 'sewers'),
    ("worm's inside.png", "worm's inside"),
]

print("生成地图训练数据...")
print("=" * 60)

total_created = 0
for map_file, map_name in maps:
    if os.path.exists(map_file):
        count = generate_map_images(map_file, map_name, num_images=64)
        total_created += count
        print(f"完成: {map_name} - {count} 张图片\n")
    else:
        print(f"文件不存在: {map_file}\n")

print(f"总共创建: {total_created} 张训练图片")
