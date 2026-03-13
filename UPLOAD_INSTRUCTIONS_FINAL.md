# 🚀 云端训练上传指令

压缩包已创建：`florr_mob_detector_training_package.tar.gz` (61MB)

## 📦 压缩包内容

```
florr_mob_detector_training_package.tar.gz (61MB)
├── mob_images/              # 77种Mob图像
├── backgrounds/             # 地图背景图像
├── dataset/                 # 验证集（可选）
├── scripts/                 # 训练脚本
│   ├── generate_data.py     # 数据生成脚本
│   ├── train_cloud.py       # 云端训练脚本（推荐）
│   └── ...
├── training_scripts/        # Jupyter Notebook
└── README.md               # 详细说明
```

---

## 🎯 Kaggle 上传（推荐）

### 方法1：网页上传

```bash
# 1. 解压
tar -xzf florr_mob_detector_training_package.tar.gz

# 2. 访问 Kaggle
# https://www.kaggle.com/datasets
# 点击 "New Dataset"

# 3. 上传整个 upload_package 文件夹
# 设置标题: florr-mob-training-package
# 可见性: Private
```

### 方法2：Kaggle API

```bash
# 1. 安装并配置 Kaggle API
pip install kaggle
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# 2. 解压
tar -xzf florr_mob_detector_training_package.tar.gz

# 3. 创建数据集
cd upload_package
kaggle datasets init -p .
# 编辑 dataset-metadata.json，设置 title 和 id

kaggle datasets create -p .
```

### Kaggle 训练命令

在 Kaggle Notebook 中：

```python
# 安装依赖
!pip install -q ultralytics

# 完整流程：数据生成 + 训练 + 验证
!python scripts/train_cloud.py \
    --mode all \
    --mob-dir ./mob_images \
    --bg-dir ./backgrounds \
    --dataset-dir ./dataset \
    --num-samples 5000 \
    --epochs 100 \
    --batch 16 \
    --project /kaggle/working/runs
```

---

## 🎯 Google Colab 上传

### 方法1：Google Drive

```bash
# 1. 解压
tar -xzf florr_mob_detector_training_package.tar.gz

# 2. 上传到 Google Drive
# 创建文件夹: florr_training
# 上传 upload_package 内容
```

### 方法2：直接上传

在 Colab Notebook 中：

```python
# 上传压缩包
from google.colab import files
uploaded = files.upload()

# 解压
!tar -xzf florr_mob_detector_training_package.tar.gz
```

### Colab 训练命令

```python
from google.colab import drive
drive.mount('/content/drive')

# 进入目录
%cd /content/drive/MyDrive/florr_training

# 安装依赖
!pip install -q ultralytics

# 训练
!python scripts/train_cloud.py \
    --mode all \
    --mob-dir ./mob_images \
    --bg-dir ./backgrounds \
    --num-samples 5000 \
    --epochs 100 \
    --batch 16
```

---

## 🎯 恒源云上传

### 上传到服务器

```bash
# 1. 上传压缩包
scp florr_mob_detector_training_package.tar.gz root@your-server-ip:/root/

# 2. SSH 登录
ssh root@your-server-ip

# 3. 解压
cd /root
tar -xzf florr_mob_detector_training_package.tar.gz
```

### 恒源云训练命令

```bash
# 安装依赖
pip install ultralytics opencv-python numpy

# 训练（更多样本，更大batch）
python upload_package/scripts/train_cloud.py \
    --mode all \
    --mob-dir upload_package/mob_images \
    --bg-dir upload_package/backgrounds \
    --num-samples 10000 \
    --epochs 150 \
    --batch 32 \
    --project /root/runs
```

---

## 📊 训练参数对比

| 平台 | GPU | 样本数 | Batch | Epochs | 时间 | 压缩包大小 |
|------|-----|--------|-------|--------|------|-----------|
| Kaggle | P100 | 5000 | 16 | 100 | 2-3h | 61MB |
| Colab | T4 | 5000 | 16 | 100 | 2-3h | 61MB |
| 恒源云 | 3090 | 10000 | 32 | 150 | 1-2h | 61MB |

---

## 🔧 运行模式

### 完整流程（推荐）
```bash
python scripts/train_cloud.py --mode all
```
自动执行：数据生成 → 训练 → 验证

### 仅生成数据
```bash
python scripts/train_cloud.py --mode generate --num-samples 5000
```

### 仅训练
```bash
python scripts/train_cloud.py --mode train --data-yaml ./dataset/data.yaml
```

### 仅验证
```bash
python scripts/train_cloud.py --mode validate --model ./runs/.../best.pt
```

---

## 📥 下载模型

### Kaggle
在 Output 区域下载 `best.pt`

### Colab
```python
from google.colab import files
files.download('runs/mob_detector_yolov8s/weights/best.pt')
```

### 恒源云
```bash
scp root@your-ip:/root/runs/mob_detector_yolov8s/weights/best.pt .
```

---

## 🎮 使用模型

```python
from ultralytics import YOLO

model = YOLO('best.pt')
results = model.predict('game_screenshot.jpg')
results[0].show()
```

---

## ⚡ 快速开始

### Kaggle（最简单）
1. 上传压缩包到 Kaggle Dataset
2. 创建 Notebook，添加数据集
3. 运行训练命令
4. 下载模型

### Colab（最灵活）
1. 上传到 Google Drive
2. 创建 Notebook，挂载 Drive
3. 运行训练命令
4. 自动保存到 Drive

### 恒源云（最快）
1. SCP 上传压缩包
2. SSH 登录并解压
3. 运行训练命令
4. SCP 下载模型

---

## 📝 注意事项

1. **压缩包大小**: 61MB（包含所有 Mob 图像和背景）
2. **训练集**: 当场合成的 5000-10000 张图片
3. **模型**: YOLOv8s（比 YOLOv8n 精度高 2-3%）
4. **时长**: Kaggle/Colab 有时长限制，建议监控训练进度

祝训练顺利！🚀
