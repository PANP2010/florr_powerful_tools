# Kaggle API 使用指南

## 📋 目录

1. [安装和配置](#1-安装和配置)
2. [上传数据集](#2-上传数据集)
3. [下载模型](#3-下载模型)
4. [常用命令](#4-常用命令)
5. [常见问题](#5-常见问题)

---

## 1. 安装和配置

### 1.1 安装 Kaggle API

```bash
# 使用 pip 安装
pip install kaggle

# 或使用 conda 安装
conda install -c conda-forge kaggle
```

### 1.2 获取 API Token

1. **登录 Kaggle**
   - 访问 https://www.kaggle.com/
   - 登录您的账号

2. **创建 API Token**
   - 点击右上角头像
   - 选择 "Settings"
   - 滚动到 "API" 部分
   - 点击 "Create New API Token"

3. **下载 kaggle.json**
   - 会自动下载 `kaggle.json` 文件
   - 文件内容示例：
     ```json
     {
       "username": "your-username",
       "key": "your-api-key"
     }
     ```

### 1.3 配置 API Token

#### macOS / Linux

```bash
# 创建 .kaggle 目录
mkdir -p ~/.kaggle

# 移动 kaggle.json 到正确位置
mv ~/Downloads/kaggle.json ~/.kaggle/

# 设置权限（重要！）
chmod 600 ~/.kaggle/kaggle.json
```

#### Windows

```powershell
# 创建 .kaggle 目录
mkdir %USERPROFILE%\.kaggle

# 移动 kaggle.json
move %USERPROFILE%\Downloads\kaggle.json %USERPROFILE%\.kaggle\

# 设置权限（右键文件 > 属性 > 安全）
```

### 1.4 验证安装

```bash
# 查看版本
kaggle --version

# 测试连接
kaggle competitions list

# 查看用户信息
kaggle config view
```

---

## 2. 上传数据集

### 2.1 准备数据集

```bash
# 解压训练包
tar -xzf florr_mob_detector_training_package.tar.gz

# 进入目录
cd upload_package
```

### 2.2 创建数据集元数据

```bash
# 初始化数据集元数据
kaggle datasets init -p .

# 这会创建 dataset-metadata.json 文件
```

### 2.3 编辑元数据

编辑 `dataset-metadata.json`：

```json
{
  "title": "Florr Mob Training Package",
  "id": "your-username/florr-mob-training-package",
  "licenses": [
    {
      "name": "CC0-1.0"
    }
  ],
  "keywords": [
    "computer-vision",
    "object-detection",
    "yolo",
    "game"
  ]
}
```

**重要**: 
- `id` 格式必须是 `username/dataset-name`
- `username` 必须是您的 Kaggle 用户名

### 2.4 上传数据集

```bash
# 创建新数据集
kaggle datasets create -p .

# 或创建并设为私有
kaggle datasets create -p . --public

# 更新现有数据集
kaggle datasets version -p . -m "Updated dataset"
```

### 2.5 完整上传脚本

创建 `upload_to_kaggle.sh`：

```bash
#!/bin/bash

# Kaggle 数据集上传脚本

DATASET_NAME="florr-mob-training-package"
USERNAME="your-username"  # 修改为您的用户名

echo "准备上传数据集到 Kaggle..."

# 检查 kaggle.json 是否存在
if [ ! -f ~/.kaggle/kaggle.json ]; then
    echo "错误: 未找到 kaggle.json"
    echo "请先下载并配置 API Token"
    exit 1
fi

# 检查数据集目录
if [ ! -d "upload_package" ]; then
    echo "错误: 未找到 upload_package 目录"
    exit 1
fi

# 进入目录
cd upload_package

# 创建元数据（如果不存在）
if [ ! -f "dataset-metadata.json" ]; then
    echo "创建数据集元数据..."
    kaggle datasets init -p .
    
    # 更新元数据
    cat > dataset-metadata.json << EOF
{
  "title": "Florr Mob Training Package",
  "id": "${USERNAME}/${DATASET_NAME}",
  "licenses": [{"name": "CC0-1.0"}]
}
EOF
fi

# 上传数据集
echo "上传数据集..."
kaggle datasets create -p .

echo "✓ 上传完成!"
echo "访问: https://www.kaggle.com/datasets/${USERNAME}/${DATASET_NAME}"
```

使用方法：

```bash
chmod +x upload_to_kaggle.sh
./upload_to_kaggle.sh
```

---

## 3. 下载模型

### 3.1 从 Kaggle Dataset 下载

```bash
# 下载数据集
kaggle datasets download -d username/dataset-name

# 解压
unzip dataset-name.zip
```

### 3.2 从 Notebook Output 下载

训练完成后，模型保存在 `/kaggle/working/`。需要先保存为 Dataset：

**在 Notebook 中运行：**

```python
# 创建模型数据集
import os
os.chdir('/kaggle/working')

# 创建元数据
!mkdir -p model_dataset
!echo '{
  "title": "Florr Mob Detector Model",
  "id": "your-username/florr-mob-detector-model",
  "licenses": [{"name": "CC0-1.0"}]
}' > model_dataset/dataset-metadata.json

# 复制模型文件
!cp runs/mob_detector_yolo26s/weights/best.pt model_dataset/

# 创建数据集
!kaggle datasets create -p model_dataset
```

**本地下载：**

```bash
# 下载模型数据集
kaggle datasets download -d your-username/florr-mob-detector-model

# 解压
unzip florr-mob-detector-model.zip
```

---

## 4. 常用命令

### 4.1 数据集操作

```bash
# 列出数据集
kaggle datasets list

# 搜索数据集
kaggle datasets list -s "yolo"

# 查看数据集信息
kaggle datasets view username/dataset-name

# 下载数据集
kaggle datasets download -d username/dataset-name

# 下载特定文件
kaggle datasets download -d username/dataset-name -f filename

# 创建数据集
kaggle datasets create -p /path/to/dataset

# 更新数据集
kaggle datasets version -p /path/to/dataset -m "Update message"

# 删除数据集（谨慎使用）
kaggle datasets delete -d username/dataset-name
```

### 4.2 Notebook 操作

```bash
# 列出 Notebooks
kaggle kernels list

# 搜索 Notebooks
kaggle kernels list -s "yolo"

# 查看 Notebook 信息
kaggle kernels pull username/notebook-name

# 下载 Notebook
kaggle kernels pull username/notebook-name -p /path/to/save

# 运行 Notebook
kaggle kernels push -p /path/to/notebook

# 查看 Notebook 输出
kaggle kernels output username/notebook-name -p /path/to/output
```

### 4.3 Competition 操作

```bash
# 列出比赛
kaggle competitions list

# 参加比赛
kaggle competitions download -c competition-name

# 提交结果
kaggle competitions submit -c competition-name -f submission.csv -m "Message"

# 查看排行榜
kaggle competitions leaderboard -c competition-name
```

### 4.4 配置操作

```bash
# 查看配置
kaggle config view

# 设置配置
kaggle config set -n path -v /path/to/kaggle

# 设置代理
kaggle config set -n proxy -v http://proxy:port
```

---

## 5. 常见问题

### Q1: 403 Forbidden 错误

**原因**: API Token 未正确配置

**解决方案**:
```bash
# 检查文件权限
ls -la ~/.kaggle/kaggle.json

# 应该显示: -rw------- (600)
# 如果不是，设置权限
chmod 600 ~/.kaggle/kaggle.json
```

### Q2: 404 Not Found 错误

**原因**: 数据集或用户名不存在

**解决方案**:
```bash
# 检查用户名
kaggle config view

# 确认数据集存在
kaggle datasets list -s "dataset-name"
```

### Q3: 上传失败

**原因**: 文件过大或网络问题

**解决方案**:
```bash
# 分批上传
# 或使用压缩
tar -czf dataset.tar.gz upload_package/

# 检查文件大小限制（单文件 20GB）
du -sh upload_package/
```

### Q4: 下载速度慢

**解决方案**:
```bash
# 使用代理
kaggle config set -n proxy -v http://your-proxy:port

# 或使用多线程下载工具
wget -c url
```

### Q5: 如何更新数据集

**解决方案**:
```bash
# 修改文件后
kaggle datasets version -p . -m "Updated files"

# 查看版本历史
kaggle datasets view username/dataset-name
```

---

## 6. Python API 使用

### 6.1 安装和导入

```python
# 安装
!pip install kaggle

# 导入
from kaggle.api.kaggle_api_extended import KaggleApi

# 认证
api = KaggleApi()
api.authenticate()
```

### 6.2 数据集操作

```python
# 列出数据集
datasets = api.dataset_list(search='yolo')
for dataset in datasets:
    print(dataset.ref, dataset.title)

# 下载数据集
api.dataset_download_files('username/dataset-name', path='./data')

# 解压
import zipfile
with zipfile.ZipFile('./data/dataset-name.zip', 'r') as zip_ref:
    zip_ref.extractall('./data')

# 创建数据集
api.dataset_create_new(
    folder='/path/to/dataset',
    public=False
)

# 更新数据集
api.dataset_create_version(
    folder='/path/to/dataset',
    version_notes='Updated dataset'
)
```

### 6.3 Notebook 操作

```python
# 列出 Notebooks
kernels = api.kernel_list(search='yolo')
for kernel in kernels:
    print(kernel.ref, kernel.title)

# 下载 Notebook
api.kernel_pull('username/notebook-name', path='./notebooks')

# 运行 Notebook
api.kernel_push(
    folder='/path/to/notebook'
)

# 获取输出
api.kernel_output('username/notebook-name', path='./output')
```

### 6.4 完整训练脚本示例

```python
from kaggle.api.kaggle_api_extended import KaggleApi
import zipfile
import os

# 认证
api = KaggleApi()
api.authenticate()

# 下载数据集
print("下载数据集...")
api.dataset_download_files(
    'your-username/florr-mob-training-package',
    path='./data'
)

# 解压
print("解压...")
with zipfile.ZipFile('./data/florr-mob-training-package.zip', 'r') as zip_ref:
    zip_ref.extractall('./data')

# 训练模型
print("训练模型...")
from ultralytics import YOLO

model = YOLO('./data/yolo26s.pt')
results = model.train(
    data='./data/dataset/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16
)

# 保存模型到新数据集
print("保存模型...")
os.makedirs('./model_output', exist_ok=True)
os.system('cp runs/mob_detector_yolo26s/weights/best.pt ./model_output/')

# 创建元数据
metadata = {
    "title": "Florr Mob Detector Model",
    "id": "your-username/florr-mob-detector-model",
    "licenses": [{"name": "CC0-1.0"}]
}

import json
with open('./model_output/dataset-metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

# 上传模型
print("上传模型...")
api.dataset_create_new(
    folder='./model_output',
    public=False
)

print("✓ 完成!")
```

---

## 7. 自动化脚本

### 7.1 自动上传和训练

创建 `auto_train.py`：

```python
#!/usr/bin/env python3
"""自动化训练脚本"""

from kaggle.api.kaggle_api_extended import KaggleApi
import subprocess
import os
import time

def main():
    # 认证
    api = KaggleApi()
    api.authenticate()
    
    # 1. 上传数据集
    print("1. 上传数据集...")
    subprocess.run([
        'kaggle', 'datasets', 'create',
        '-p', 'upload_package',
        '--public'
    ])
    
    # 2. 创建 Notebook
    print("2. 创建 Notebook...")
    # 这里需要手动在 Kaggle 网页上创建
    
    # 3. 运行 Notebook
    print("3. 运行 Notebook...")
    subprocess.run([
        'kaggle', 'kernels', 'push',
        '-p', 'kaggle_notebook'
    ])
    
    # 4. 等待完成
    print("4. 等待训练完成...")
    while True:
        status = api.kernel_status('your-username/notebook-name')
        if status == 'complete':
            break
        time.sleep(60)
    
    # 5. 下载结果
    print("5. 下载结果...")
    subprocess.run([
        'kaggle', 'kernels', 'output',
        'your-username/notebook-name',
        '-p', 'output'
    ])
    
    print("✓ 完成!")

if __name__ == '__main__':
    main()
```

---

## 📊 API 限制

| 操作 | 限制 |
|------|------|
| 数据集上传 | 单文件 20GB |
| Notebook 运行 | 12 小时 |
| API 请求 | 1000 次/天 |
| 下载速度 | 无限制 |

---

## 🔗 有用链接

- Kaggle API 文档: https://github.com/Kaggle/kaggle-api
- Kaggle 官方文档: https://www.kaggle.com/docs/api
- API 参考: https://www.kaggle.com/docs/api

---

祝使用顺利！🚀
