from PIL import Image
import cv2
import numpy as np
import os

def analyze_map(image_path):
    img = Image.open(image_path)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    print(f"\n地图: {image_path}")
    print(f"尺寸: {img.size}")
    print(f"模式: {img.mode}")
    
    if img.mode == 'RGBA':
        img_rgb = img.convert('RGB')
        img_cv = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2BGR)
    
    h, w = img_cv.shape[:2]
    print(f"高度: {h}, 宽度: {w}")
    
    corners = [
        (0, 0),
        (w-1, 0),
        (0, h-1),
        (w-1, h-1),
        (w//2, 0),
        (0, h//2),
        (w//2, h//2)
    ]
    
    print("角落像素颜色:")
    for x, y in corners:
        if 0 <= x < w and 0 <= y < h:
            if img.mode == 'RGBA':
                pixel = img.getpixel((x, y))[:3]
            else:
                pixel = img.getpixel((x, y))
            hex_color = '#{:02x}{:02x}{:02x}'.format(*pixel)
            print(f"  ({x:3d}, {y:3d}): {pixel} ({hex_color})")
    
    if img.mode == 'RGBA':
        alpha = np.array(img.split()[3])
        unique_alphas = np.unique(alpha)
        print(f"Alpha通道值: {unique_alphas}")
    
    return img_cv

maps_to_analyze = [
    'factory.png',
    'garden.png',
    'sewers.png',
    "worm's inside.png"
]

print("分析新地图...")
print("=" * 60)

for map_file in maps_to_analyze:
    if map_file.endswith('.png') and os.path.exists(map_file):
        analyze_map(map_file)
