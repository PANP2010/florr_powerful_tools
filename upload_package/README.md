# Florr.io Mob 检测器云端训练包

完整的云端训练解决方案，支持数据生成和模型训练一体化。

## 📦 包内容

```
upload_package/
├── mob_images/              # 77种Mob图像
├── backgrounds/             # 地图背景图像
├── dataset/                 # 验证集（可选）
│   ├── val/labels/
│   ├── data.yaml
│   └── data_cloud.yaml
├── scripts/                 # 训练脚本
│   ├── generate_data.py     # 数据生成脚本
│   ├── train.py             # 本地训练脚本
│   ├── train_cloud.py       # 云端训练脚本（推荐）
│   └── validate_coverage.py # 覆盖验证
├── training_scripts/        # Jupyter Notebook
│   ├── train_mob_detector_colab.py
│   └── train_mob_detector_notebook.ipynb
└── README.md               # 本文件
```

## 🚀 快速开始

### Kaggle（推荐）

#### 1. 上传数据包
```bash
# 解压
tar -xzf florr_mob_detector_training_package.tar.gz

# 使用 Kaggle API 上传
cd upload_package
kaggle datasets create -p .
```

或访问 https://www.kaggle.com/datasets 网页上传整个 `upload_package` 文件夹。

#### 2. 创建 Notebook 并训练

在 Kaggle Notebook 中：

```python
# 安装依赖
!pip install -q ultralytics

# 运行云端训练脚本
!python scripts/train_cloud.py \
    --mode all \
    --mob-dir ./mob_images \
    --bg-dir ./backgrounds \
    --dataset-dir ./dataset \
    --num-samples 5000 \
    --epochs 100 \
    --batch 16
```

### Google Colab

#### 1. 上传到 Google Drive

```bash
# 解压
tar -xzf florr_mob_detector_training_package.tar.gz

# 上传到 Google Drive 的 florr_training 文件夹
```

#### 2. 在 Colab 中训练

```python
from google.colab import drive
drive.mount('/content/drive')

# 进入目录
%cd /content/drive/MyDrive/florr_training

# 安装依赖
!pip install -q ultralytics

# 运行训练
!python scripts/train_cloud.py \
    --mode all \
    --mob-dir ./mob_images \
    --bg-dir ./backgrounds \
    --num-samples 5000 \
    --epochs 100 \
    --batch 16
```

### 恒源云

#### 1. 上传到服务器

```bash
# 上传压缩包
scp florr_mob_detector_training_package.tar.gz root@your-ip:/root/

# SSH 登录并解压
ssh root@your-ip
cd /root
tar -xzf florr_mob_detector_training_package.tar.gz
```

#### 2. 训练

```bash
# 安装依赖
pip install ultralytics opencv-python numpy

# 运行训练（更多样本和更大batch）
python upload_package/scripts/train_cloud.py \
    --mode all \
    --mob-dir upload_package/mob_images \
    --bg-dir upload_package/backgrounds \
    --num-samples 10000 \
    --epochs 150 \
    --batch 32
```

## 📊 训练参数建议

| 平台 | GPU | 样本数 | Batch | Epochs | 预计时间 |
|------|-----|--------|-------|--------|----------|
| Kaggle | P100 | 5000 | 16 | 100 | 2-3小时 |
| Colab | T4 | 5000 | 16 | 100 | 2-3小时 |
| 恒源云 | 3090 | 10000 | 32 | 150 | 1-2小时 |

## 🔧 运行模式

### 1. 完整流程（推荐）
```bash
python scripts/train_cloud.py --mode all
```
自动执行：数据生成 → 训练 → 验证

### 2. 仅生成数据
```bash
python scripts/train_cloud.py --mode generate --num-samples 5000
```

### 3. 仅训练（使用现有数据）
```bash
python scripts/train_cloud.py --mode train --data-yaml ./dataset/data.yaml
```

### 4. 仅验证
```bash
python scripts/train_cloud.py --mode validate --model ./runs/mob_detector_yolov8s/weights/best.pt
```

## 🎯 YOLOv8s vs YOLOv8n

| 特性 | YOLOv8n | YOLOv8s | 提升 |
|------|---------|---------|------|
| 参数量 | 3.2M | 11.2M | +250% |
| 模型大小 | 6.3MB | 22MB | +250% |
| mAP | 基准 | +2-3% | 更高精度 |
| 显存需求 | 4GB | 8GB | 需要更多显存 |
| 推理速度 | 快 | 中等 | 稍慢 |

## 📋 数据生成参数

- **样本数量**: 5000-10000（根据平台选择）
- **训练/验证比例**: 85% / 15%
- **每张图怪物数**: 5-20
- **怪物缩放范围**: 0.06-0.5
- **数据增强**: 旋转、亮度调整、噪声

## 🔍 验证结果示例

训练完成后会显示：

```
验证结果:
  mAP50: 0.9234
  mAP50-95: 0.7856
  Precision: 0.8912
  Recall: 0.8765
```

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

## 🎮 使用模型

```python
from ultralytics import YOLO

# 加载模型
model = YOLO('best.pt')

# 预测
results = model.predict('game_screenshot.jpg')

# 显示结果
results[0].show()

# 获取检测框
boxes = results[0].boxes
for box in boxes:
    class_id = int(box.cls[0])
    class_name = results[0].names[class_id]
    confidence = float(box.conf[0])
    print(f"{class_name}: {confidence:.2f}")
```

## ⚠️ 注意事项

1. **显存不足**: 减小 batch size（16→8→4）
2. **训练时间**: Kaggle/Colab 有时长限制，建议分批训练
3. **数据质量**: 确保所有 mob 图像都有透明背景（PNG格式）
4. **断点续训**: 使用 `--resume` 参数继续训练

## 🐛 常见问题

### Q: 如何继续训练？
```bash
python scripts/train_cloud.py --mode train --resume runs/mob_detector_yolov8s/weights/last.pt
```

### Q: 如何调整学习率？
修改 `train_cloud.py` 中的 `lr0` 参数。

### Q: 如何添加新的 Mob？
1. 将图像添加到 `mob_images/` 目录
2. 更新 `generate_data.py` 中的 `MAP_MOBS` 配置
3. 重新生成数据集

## 📞 需要帮助？

检查以下内容：
1. GPU 是否可用：`torch.cuda.is_available()`
2. 数据集路径是否正确
3. 图像格式是否为 PNG（透明背景）
4. 依赖是否完整安装

祝训练顺利！🚀
