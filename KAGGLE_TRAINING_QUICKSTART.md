# 🎉 Kaggle 训练快速开始指南

## ✅ 已完成

- 数据集已上传到 Kaggle
- 数据集 ID: `panp2010/florr-mob-training-package`

---

## 📝 下一步：创建 Notebook 并训练

### 步骤 1: 创建 Notebook

1. **访问 Kaggle Code**
   - 打开 https://www.kaggle.com/code
   - 点击右上角 "New Notebook"

2. **设置运行环境**
   - 在右侧面板中：
     - **Accelerator**: GPU P100 或 GPU T4 ✅
     - **Language**: Python
     - **Persistence**: Files only

---

### 步骤 2: 添加数据集

1. **添加您的数据集**
   - 点击右侧 "Add Data" 按钮
   - 搜索: `florr-mob-training-package`
   - 找到您的数据集
   - 点击 "Add" 按钮

2. **验证数据集路径**
   - 数据集会被挂载到: `/kaggle/input/florr-mob-training-package/`

---

### 步骤 3: 复制训练代码

在 Notebook 中创建新的代码单元格，复制以下代码：

#### 单元格 1: 环境检查

```python
import torch
print("=" * 60)
print("环境检查")
print("=" * 60)
print(f"PyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"✓ GPU型号: {torch.cuda.get_device_name(0)}")
    print(f"✓ 显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("✗ GPU不可用，请检查设置")
```

#### 单元格 2: 安装依赖

```python
print("安装依赖...")
!pip install -q ultralytics
print("✓ 安装完成")

from ultralytics import YOLO
print("✓ 导入成功")
```

#### 单元格 3: 配置路径

```python
import os

# 数据集路径
DATASET_PATH = '/kaggle/input/florr-mob-training-package'
WORK_PATH = '/kaggle/working'

# 训练参数
NUM_SAMPLES = 5000  # 训练样本数
EPOCHS = 100        # 训练轮数
BATCH_SIZE = 16     # Batch size

print(f"数据集路径: {DATASET_PATH}")
print(f"工作路径: {WORK_PATH}")

# 检查数据集
if os.path.exists(DATASET_PATH):
    print("✓ 数据集已找到")
    print("\n数据集内容:")
    for item in os.listdir(DATASET_PATH)[:10]:
        print(f"  - {item}")
else:
    print("✗ 数据集未找到")
```

#### 单元格 4: 生成训练数据

```python
import sys
sys.path.append(f'{DATASET_PATH}/scripts')

from generate_data import HighQualityDataGenerator

print("=" * 60)
print("生成训练数据")
print("=" * 60)

generator = HighQualityDataGenerator(
    mob_dir=f'{DATASET_PATH}/mob_images',
    bg_dir=f'{DATASET_PATH}/backgrounds',
    output_dir=f'{WORK_PATH}/dataset'
)

generator.generate_dataset(
    total_samples=NUM_SAMPLES,
    train_ratio=0.85,
    num_mobs_range=(5, 20),
    scale_range=(0.06, 0.5)
)

print("\n✓ 数据集生成完成")
```

#### 单元格 5: 训练模型

```python
print("=" * 60)
print("训练 YOLO26s 模型")
print("=" * 60)

# 加载预训练模型
model = YOLO(f'{DATASET_PATH}/yolo26s.pt')

print(f"\n训练参数:")
print(f"  - 样本数: {NUM_SAMPLES}")
print(f"  - Epochs: {EPOCHS}")
print(f"  - Batch size: {BATCH_SIZE}")

print("\n开始训练...")

# 训练
results = model.train(
    data=f'{WORK_PATH}/dataset/data.yaml',
    epochs=EPOCHS,
    imgsz=640,
    batch=BATCH_SIZE,
    name='mob_detector_yolo26s',
    project=f'{WORK_PATH}/runs',
    device='cuda',
    patience=20,
    save=True,
    plots=True,
)

print("\n✓ 训练完成!")
```

#### 单元格 6: 验证模型

```python
print("=" * 60)
print("验证模型")
print("=" * 60)

metrics = model.val()

print(f"\n验证结果:")
print(f"  mAP50: {metrics.box.map50:.4f}")
print(f"  mAP50-95: {metrics.box.map:.4f}")
print(f"  Precision: {metrics.box.mp:.4f}")
print(f"  Recall: {metrics.box.mr:.4f}")
```

#### 单元格 7: 保存模型

```python
import shutil
from pathlib import Path

print("=" * 60)
print("保存模型")
print("=" * 60)

# 打包训练结果
shutil.make_archive(
    f'{WORK_PATH}/mob_detector_results',
    'zip',
    f'{WORK_PATH}/runs/mob_detector_yolo26s'
)

print("✓ 打包完成: mob_detector_results.zip")

# 显示输出文件
print("\n输出文件:")
for item in os.listdir(WORK_PATH):
    item_path = os.path.join(WORK_PATH, item)
    if os.path.isfile(item_path):
        size = os.path.getsize(item_path) / 1024 / 1024
        print(f"  📄 {item} ({size:.2f} MB)")
```

---

### 步骤 4: 运行训练

1. **运行所有单元格**
   - 点击菜单 "Run" → "Run All"
   - 或按快捷键 `Ctrl + Enter` 逐个运行

2. **监控训练进度**
   - 查看输出日志
   - 预计训练时间: 2-3 小时

3. **等待完成**
   - 训练会自动保存最佳模型
   - 完成后会显示验证结果

---

### 步骤 5: 下载模型

训练完成后：

1. **查看输出文件**
   - 点击右侧 "Output" 标签
   - 找到以下文件:
     - `mob_detector_results.zip` - 完整训练结果
     - `runs/mob_detector_yolo26s/weights/best.pt` - 最佳模型

2. **下载模型**
   - 点击文件右侧的下载图标
   - 或勾选多个文件批量下载

---

## 📊 训练时间参考

| GPU | 样本数 | Batch | Epochs | 预计时间 |
|-----|--------|-------|--------|----------|
| P100 | 5000 | 16 | 100 | 2-3小时 |
| T4 | 5000 | 16 | 100 | 2-3小时 |

---

## ⚠️ 注意事项

1. **GPU 设置**
   - 确保选择了 GPU P100 或 T4
   - 免费版有 30 小时/周 限制

2. **运行时长**
   - Notebook 有 12 小时运行限制
   - 训练应在 2-3 小时内完成

3. **保存进度**
   - 模型会自动保存
   - 可以使用 `last.pt` 继续训练

---

## 🎯 训练完成后

下载 `best.pt` 模型文件后：

```python
from ultralytics import YOLO

# 加载模型
model = YOLO('best.pt')

# 预测
results = model.predict('game_screenshot.jpg')
results[0].show()
```

---

## 📞 需要帮助？

如果遇到问题：
1. 检查 GPU 是否可用
2. 确认数据集路径正确
3. 查看错误日志

祝训练顺利！🚀
