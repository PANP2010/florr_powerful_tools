# Florr.io Mob 检测器云端训练包

完整的云端训练解决方案，使用 **Ultralytics YOLO26s** 最新模型。

## 📦 包内容

```
upload_package/
├── mob_images/              # 77种Mob图像
├── backgrounds/             # 地图背景图像
├── dataset/                 # 验证集（可选）
├── scripts/                 # 训练脚本
│   ├── generate_data.py     # 数据生成脚本
│   ├── train_cloud.py       # 云端训练脚本（推荐）⭐
│   └── ...
└── training_scripts/        # 其他训练脚本
```

## 🚀 YOLO26s 特点

YOLO26 是 Ultralytics 2025 年最新发布的模型：

| 特性 | YOLOv8s | YOLO26s | 提升 |
|------|---------|---------|------|
| mAP50-95 | 44.8% | 48.6% | +3.8% |
| 参数量 | 11.2M | 9.5M | -15% |
| CPU推理速度 | 基准 | +43% | 更快 |
| 端到端推理 | 需要 NMS | 无需 NMS | 更简洁 |
| 边缘部署 | 一般 | 优化 | 更适合 |

**核心优势：**
- ✅ 端到端无 NMS 推理
- ✅ CPU 推理速度提升 43%
- ✅ 小目标检测精度更高
- ✅ 更适合边缘设备部署

## 🎯 快速开始

### Kaggle（推荐）

```python
# 安装依赖
!pip install -q ultralytics

# 完整流程：数据生成 + 训练 + 验证
!python scripts/train_cloud.py \
    --mode all \
    --mob-dir ./mob_images \
    --bg-dir ./backgrounds \
    --num-samples 5000 \
    --epochs 100 \
    --batch 16
```

### Google Colab

```python
from google.colab import drive
drive.mount('/content/drive')

%cd /content/drive/MyDrive/florr_training
!pip install -q ultralytics

!python scripts/train_cloud.py --mode all --num-samples 5000
```

### 恒源云

```bash
pip install ultralytics opencv-python numpy

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

```bash
# 完整流程（推荐）
python scripts/train_cloud.py --mode all

# 仅生成数据
python scripts/train_cloud.py --mode generate --num-samples 5000

# 仅训练
python scripts/train_cloud.py --mode train --data-yaml ./dataset/data.yaml

# 仅验证
python scripts/train_cloud.py --mode validate --model ./runs/.../best.pt
```

## 📥 下载模型

### Kaggle
在 Output 区域下载 `best.pt`

### Colab
```python
from google.colab import files
files.download('runs/mob_detector_yolo26s/weights/best.pt')
```

### 恒源云
```bash
scp root@your-ip:/root/runs/mob_detector_yolo26s/weights/best.pt .
```

## 🎮 使用模型

```python
from ultralytics import YOLO

# 加载模型
model = YOLO('best.pt')

# 预测（端到端，无需 NMS）
results = model.predict('game_screenshot.jpg')
results[0].show()

# 获取检测结果
boxes = results[0].boxes
for box in boxes:
    class_name = results[0].names[int(box.cls[0])]
    confidence = float(box.conf[0])
    print(f"{class_name}: {confidence:.2f}")
```

## 📝 注意事项

1. **Ultralytics 版本**: 需要 `ultralytics>=8.3.0` 支持 YOLO26
2. **显存需求**: YOLO26s 需要约 8GB 显存
3. **训练集**: 当场合成的 5000-10000 张图片
4. **端到端推理**: YOLO26 原生支持无 NMS 推理

## 🆕 YOLO26 新特性

- **DFL 移除**: 简化推理，提高硬件兼容性
- **MuSGD 优化器**: 更稳定的训练，更快的收敛
- **ProgLoss + STAL**: 小目标检测精度提升
- **原生端到端**: 无需 NMS 后处理

祝训练顺利！🚀
