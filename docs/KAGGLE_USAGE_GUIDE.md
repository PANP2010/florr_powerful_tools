# Kaggle 使用指南 - YOLO26s Mob 检测器训练

## 📋 目录

1. [注册 Kaggle 账号](#1-注册-kaggle-账号)
2. [上传数据集](#2-上传数据集)
3. [创建 Notebook](#3-创建-notebook)
4. [运行训练](#4-运行训练)
5. [下载模型](#5-下载模型)
6. [常见问题](#6-常见问题)

---

## 1. 注册 Kaggle 账号

### 步骤：

1. 访问 https://www.kaggle.com/
2. 点击右上角 "Register"
3. 选择注册方式：
   - Google 账号（推荐）
   - Email 注册
4. 完成手机验证（需要接收验证码）

### ⚠️ 重要提示

- **手机验证是必须的**，否则无法使用 GPU
- 建议使用 Google 账号，登录更方便

---

## 2. 上传数据集

### 方法A：网页上传（推荐）

#### 步骤：

1. **解压本地压缩包**
   ```bash
   tar -xzf florr_mob_detector_training_package.tar.gz
   ```

2. **访问 Kaggle Datasets**
   - 登录 Kaggle
   - 点击左侧菜单 "Datasets"
   - 点击右上角 "New Dataset"

3. **上传文件**
   - 拖拽 `upload_package` 文件夹到上传区域
   - 或点击 "Browse" 选择文件夹

4. **设置信息**
   - **Title**: `florr-mob-training-package`
   - **Subtitle**: `Florr.io Mob Detection Training Package with YOLO26s`
   - **Visibility**: Private（推荐）或 Public
   - **Tags**: 添加 `computer-vision`, `object-detection`, `yolo`

5. **创建**
   - 点击 "Create" 按钮
   - 等待上传完成（约 5-10 分钟）

### 方法B：Kaggle API 上传

#### 步骤：

1. **安装 Kaggle API**
   ```bash
   pip install kaggle
   ```

2. **获取 API Token**
   - 访问 https://www.kaggle.com/settings
   - 滚动到 "API" 部分
   - 点击 "Create New API Token"
   - 下载 `kaggle.json` 文件

3. **配置 API**
   ```bash
   mkdir -p ~/.kaggle
   mv ~/Downloads/kaggle.json ~/.kaggle/
   chmod 600 ~/.kaggle/kaggle.json
   ```

4. **上传数据集**
   ```bash
   cd upload_package
   
   # 初始化数据集元数据
   kaggle datasets init -p .
   
   # 编辑 dataset-metadata.json
   # 设置 title 和 id（格式：username/dataset-name）
   
   # 创建数据集
   kaggle datasets create -p .
   ```

---

## 3. 创建 Notebook

### 步骤：

1. **创建新 Notebook**
   - 点击左侧菜单 "Code"
   - 点击右上角 "New Notebook"

2. **设置运行环境**
   - 在右侧面板中：
     - **Accelerator**: GPU P100 或 GPU T4
     - **Language**: Python
     - **Environment**: 最新的 Python 环境
     - **Persistence**: Files only（推荐）

3. **添加数据集**
   - 点击右侧 "Add Data"
   - 搜索您上传的数据集：`florr-mob-training-package`
   - 点击 "Add" 添加到 Notebook

4. **上传训练脚本（可选）**
   - 如果数据集已包含训练脚本，跳过此步
   - 否则，点击 "File" > "Import Notebook"
   - 上传 `train_mob_detector_notebook.ipynb`

---

## 4. 运行训练

### 方法A：使用 Notebook（推荐）

在 Notebook 中运行以下代码：

```python
# 单元格 1: 检查环境
import torch
print(f"PyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU型号: {torch.cuda.get_device_name(0)}")
    print(f"显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
```

```python
# 单元格 2: 安装依赖
!pip install -q ultralytics
print("✓ Ultralytics 安装完成")
```

```python
# 单元格 3: 查看数据集
import os

# 数据集路径（修改为您的数据集名称）
dataset_path = '/kaggle/input/florr-mob-training-package'

# 列出内容
for root, dirs, files in os.walk(dataset_path):
    level = root.replace(dataset_path, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    for file in files[:5]:  # 只显示前5个文件
        print(f'{subindent}{file}')
    if len(files) > 5:
        print(f'{subindent}... ({len(files) - 5} more files)')
```

```python
# 单元格 4: 运行训练
# 方式1: 使用训练脚本
!python /kaggle/input/florr-mob-training-package/scripts/train_cloud.py \
    --mode all \
    --mob-dir /kaggle/input/florr-mob-training-package/mob_images \
    --bg-dir /kaggle/input/florr-mob-training-package/backgrounds \
    --dataset-dir /kaggle/working/dataset \
    --num-samples 5000 \
    --epochs 100 \
    --batch 16 \
    --project /kaggle/working/runs

# 方式2: 直接在 Notebook 中训练
from ultralytics import YOLO

# 加载模型（使用数据集中的预训练模型）
model = YOLO('/kaggle/input/florr-mob-training-package/yolo26s.pt')

# 生成数据集
import sys
sys.path.append('/kaggle/input/florr-mob-training-package/scripts')
from generate_data import HighQualityDataGenerator

generator = HighQualityDataGenerator(
    '/kaggle/input/florr-mob-training-package/mob_images',
    '/kaggle/input/florr-mob-training-package/backgrounds',
    '/kaggle/working/dataset'
)

generator.generate_dataset(
    total_samples=5000,
    train_ratio=0.85,
    num_mobs_range=(5, 20),
    scale_range=(0.06, 0.5)
)

# 训练
results = model.train(
    data='/kaggle/working/dataset/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='mob_detector_yolo26s',
    project='/kaggle/working/runs',
    device='cuda',
    patience=20,
    save=True,
    plots=True,
)

# 验证
metrics = model.val()
print(f"mAP50: {metrics.box.map50:.4f}")
print(f"mAP50-95: {metrics.box.map:.4f}")
```

### 方法B：使用命令行

在 Notebook 中运行：

```python
# 切换到工作目录
import os
os.chdir('/kaggle/working')

# 运行训练脚本
!python /kaggle/input/florr-mob-training-package/scripts/train_cloud.py \
    --mode all \
    --mob-dir /kaggle/input/florr-mob-training-package/mob_images \
    --bg-dir /kaggle/input/florr-mob-training-package/backgrounds \
    --num-samples 5000 \
    --epochs 100 \
    --batch 16
```

---

## 5. 下载模型

### 方法A：从 Output 下载

1. **查看输出文件**
   - 训练完成后，点击右侧 "Output" 标签
   - 展开 `/kaggle/working/` 目录
   - 找到 `runs/mob_detector_yolo26s/weights/best.pt`

2. **下载模型**
   - 点击文件右侧的下载图标
   - 或勾选多个文件，点击 "Download"

### 方法B：打包下载

```python
# 打包所有训练结果
import shutil
shutil.make_archive('/kaggle/working/mob_detector_results', 'zip', 
                    '/kaggle/working/runs/mob_detector_yolo26s')

print("✓ 打包完成: mob_detector_results.zip")
```

然后从 Output 下载 `mob_detector_results.zip`

### 方法C：保存到 Kaggle Dataset

```python
# 创建新数据集保存模型
!kaggle datasets create -p /kaggle/working/runs/mob_detector_yolo26s
```

---

## 6. 常见问题

### Q1: GPU 不可用怎么办？

**解决方案：**
1. 确保已完成手机验证
2. 在 Notebook 设置中选择 GPU P100 或 GPU T4
3. 检查是否超出免费时长限制（30小时/周）

### Q2: 训练中断怎么办？

**解决方案：**
1. Kaggle Notebook 有 12 小时运行限制
2. 使用 `--resume` 参数继续训练：
   ```python
   model = YOLO('/kaggle/working/runs/mob_detector_yolo26s/weights/last.pt')
   results = model.train(resume=True)
   ```
3. 定期保存模型到 Output

### Q3: 显存不足怎么办？

**解决方案：**
```python
# 减小 batch size
!python scripts/train_cloud.py --batch 8  # 从 16 改为 8

# 或减小图像尺寸
!python scripts/train_cloud.py --imgsz 512  # 从 640 改为 512
```

### Q4: 如何监控训练进度？

**解决方案：**
1. 查看 Notebook 输出日志
2. 训练完成后查看 `/kaggle/working/runs/mob_detector_yolo26s/` 中的图表
3. 使用 TensorBoard（需要额外配置）

### Q5: 数据集上传失败？

**解决方案：**
1. 检查文件大小（Kaggle 单文件限制 20GB）
2. 使用 Kaggle API 上传
3. 分批上传文件

### Q6: 如何使用多个 GPU？

**解决方案：**
Kaggle 免费版只提供单 GPU，无法使用多 GPU。

### Q7: 训练速度慢？

**解决方案：**
1. 确保使用 GPU（检查 `torch.cuda.is_available()`）
2. 减少数据生成样本数（5000 → 3000）
3. 使用混合精度训练（默认已启用）

---

## 📊 训练时间参考

| 平台 | GPU | 样本数 | Batch | Epochs | 预计时间 |
|------|-----|--------|-------|--------|----------|
| Kaggle | P100 | 5000 | 16 | 100 | 2-3小时 |
| Kaggle | T4 | 5000 | 16 | 100 | 2-3小时 |

---

## 🎯 最佳实践

1. **定期保存模型**
   - 每 10-20 个 epoch 保存一次
   - 使用 `save_period=10` 参数

2. **监控显存使用**
   ```python
   import torch
   print(f"显存使用: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
   ```

3. **使用早停**
   - 设置 `patience=20` 防止过拟合
   - 自动保存最佳模型

4. **保存训练日志**
   ```python
   # 复制训练日志到 Output
   !cp -r runs/mob_detector_yolo26s /kaggle/working/
   ```

---

## 🔗 有用链接

- Kaggle 官方文档: https://www.kaggle.com/docs
- Kaggle GPU 限制: https://www.kaggle.com/docs/notebooks#notebooks-gpu
- Ultralytics 文档: https://docs.ultralytics.com/
- YOLO26 文档: https://docs.ultralytics.com/zh/models/yolo26/

---

## 📞 需要帮助？

如果遇到问题：
1. 查看 Kaggle 官方文档
2. 检查 Notebook 输出日志
3. 访问 Ultralytics 社区: https://community.ultralytics.com/

祝训练顺利！🚀
