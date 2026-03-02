from PIL import Image
import os

webp_files = [
    'factory.webp',
    'garden.webp',
    'sewers.webp',
    "worm's inside.webp"
]

print("转换 WebP 到 PNG...")
print()

for webp_file in webp_files:
    if os.path.exists(webp_file):
        try:
            img = Image.open(webp_file)
            print(f"文件: {webp_file}")
            print(f"  原始尺寸: {img.size}")
            print(f"  原始模式: {img.mode}")
            
            png_name = webp_file.replace('.webp', '.png')
            img.save(png_name)
            print(f"  已保存: {png_name}")
            
            saved_img = Image.open(png_name)
            print(f"  保存后尺寸: {saved_img.size}")
            print()
        except Exception as e:
            print(f"错误: {webp_file} - {e}")
    else:
        print(f"文件不存在: {webp_file}")
