#!/usr/bin/env python3
"""使用 requests 下载 YOLO26s 模型"""

import requests
import os
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("正在下载 YOLO26s 模型...")

# 可能的下载链接
urls = [
    "https://github.com/ultralytics/assets/releases/download/v26.0.0/yolo26s.pt",
    "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo26s.pt",
]

output_path = "upload_package/yolo26s.pt"

for url in urls:
    try:
        print(f"\n尝试: {url}")
        
        # 使用 requests，忽略 SSL 验证
        response = requests.get(url, verify=False, stream=True, timeout=30)
        
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            
            if total_size < 1000000:  # 小于 1MB
                print(f"✗ 文件太小 ({total_size} bytes)，可能不是正确的模型文件")
                continue
            
            print(f"文件大小: {total_size / 1024 / 1024:.2f} MB")
            
            # 下载文件
            with open(output_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%", end='')
            
            print(f"\n✓ 下载成功!")
            print(f"保存到: {output_path}")
            
            # 验证文件
            size = os.path.getsize(output_path)
            print(f"文件大小: {size / 1024 / 1024:.2f} MB")
            break
        else:
            print(f"✗ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        continue
else:
    print("\n所有下载链接都失败了")
    print("\n请手动下载:")
    print("1. 访问 https://github.com/ultralytics/assets/releases")
    print("2. 找到 v26.0.0 或最新版本")
    print("3. 下载 yolo26s.pt")
    print("4. 放到 upload_package/ 目录")
