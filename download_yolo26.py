#!/usr/bin/env python3
"""下载 YOLO26s 模型文件"""

import urllib.request
import ssl
import os

# 忽略 SSL 证书验证
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 模型下载链接
model_urls = [
    "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo26s.pt",
    "https://github.com/ultralytics/assets/releases/download/v26.0.0/yolo26s.pt",
]

output_path = "upload_package/yolo26s.pt"

print("正在下载 YOLO26s 模型...")

for url in model_urls:
    try:
        print(f"尝试: {url}")
        urllib.request.urlretrieve(url, output_path)
        
        # 检查文件大小
        size = os.path.getsize(output_path)
        if size > 1000000:  # 大于 1MB
            print(f"✓ 下载成功! 文件大小: {size / 1024 / 1024:.2f} MB")
            break
        else:
            print(f"✗ 文件太小 ({size} bytes)，可能下载失败")
            os.remove(output_path)
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        continue
else:
    print("\n所有下载链接都失败了")
    print("请手动下载模型文件:")
    print("1. 访问 https://github.com/ultralytics/assets/releases")
    print("2. 下载 yolo26s.pt")
    print("3. 放到 upload_package/ 目录")
