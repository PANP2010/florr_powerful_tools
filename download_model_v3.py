#!/usr/bin/env python3
"""下载 YOLO26s 模型 - v8.4.0"""

import requests
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("正在下载 YOLO26s 模型 (v8.4.0)...\n")

# 正确的下载链接 - v8.4.0
urls = [
    "https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26s.pt",
]

output_path = "upload_package/yolo26s.pt"

for url in urls:
    try:
        print(f"尝试: {url}")
        
        response = requests.get(url, verify=False, stream=True, timeout=60)
        
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            
            if total_size < 1000000:
                print(f"✗ 文件太小 ({total_size} bytes)")
                continue
            
            print(f"文件大小: {total_size / 1024 / 1024:.2f} MB")
            
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
            
            size = os.path.getsize(output_path)
            print(f"保存到: {output_path}")
            print(f"文件大小: {size / 1024 / 1024:.2f} MB")
            break
        else:
            print(f"✗ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"✗ 失败: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        continue
else:
    print("\n下载失败，请手动下载:")
    print("https://github.com/ultralytics/assets/releases/tag/v8.4.0")
