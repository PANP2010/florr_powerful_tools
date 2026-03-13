#!/usr/bin/env python3
"""使用 Ultralytics 下载 YOLO26s 模型"""

import ssl
import urllib.request

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

print("正在下载 YOLO26s 模型...")

try:
    from ultralytics import YOLO
    print("✓ Ultralytics 已安装")
    
    # 这会自动下载模型
    model = YOLO('yolo26s.pt')
    print("✓ 模型下载成功!")
    
    # 获取模型路径
    model_path = model.ckpt_path
    print(f"模型路径: {model_path}")
    
    # 复制到 upload_package
    import shutil
    import os
    
    # 查找模型文件
    possible_paths = [
        model_path,
        os.path.expanduser('~/.cache/ultralytics/yolo26s.pt'),
        'yolo26s.pt',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size > 1000000:  # 大于 1MB
                print(f"找到模型文件: {path} ({size / 1024 / 1024:.2f} MB)")
                shutil.copy(path, 'upload_package/yolo26s.pt')
                print(f"✓ 已复制到 upload_package/yolo26s.pt")
                break
    else:
        print("未找到模型文件，请手动查找")
        
except ImportError:
    print("✗ Ultralytics 未安装")
    print("请运行: pip install ultralytics")
except Exception as e:
    print(f"✗ 下载失败: {e}")
