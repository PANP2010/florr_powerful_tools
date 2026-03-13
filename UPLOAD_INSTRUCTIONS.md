# 上传指令大全

压缩包已创建：`florr_mob_detector_training_package.tar.gz` (31KB)

## 📦 压缩包内容

```
florr_mob_detector_training_package.tar.gz
├── dataset/                    # 数据集（当前只有验证集）
│   ├── val/labels/            # 验证集标签
│   ├── data.yaml              # 本地配置
│   └── data_cloud.yaml        # 云端配置模板
├── training_scripts/          # 训练脚本
│   ├── train_mob_detector_colab.py
│   └── train_mob_detector_notebook.ipynb
└── README.md                  # 详细说明文档
```

---

## 🚀 Kaggle 上传指令

### 方法1：网页上传（推荐）

1. **解压压缩包**
   ```bash
   tar -xzf florr_mob_detector_training_package.tar.gz
   ```

2. **访问 Kaggle**
   - 打开 https://www.kaggle.com/datasets
   - 点击右上角 "New Dataset"

3. **上传文件**
   - 拖拽 `upload_package` 文件夹到上传区域
   - 或点击 "Upload" 选择文件夹

4. **设置信息**
   - Title: `florr-mob-dataset`
   - Subtitle: `Florr.io Mob Detection Dataset`
   - Visibility: Private（推荐）

5. **创建**
   - 点击 "Create" 完成

### 方法2：Kaggle API

```bash
# 1. 安装 Kaggle API
pip install kaggle

# 2. 配置 API Key
# 访问 https://www.kaggle.com/settings
# 点击 "Create New API Token" 下载 kaggle.json
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# 3. 解压并准备
tar -xzf florr_mob_detector_training_package.tar.gz
cd upload_package

# 4. 初始化数据集
kaggle datasets init -p dataset

# 5. 编辑 meta-data（会生成 dataset/dataset-metadata.json）
# 修改 title 和 id

# 6. 创建数据集
kaggle datasets create -p dataset
```

---

## 🚀 Google Colab 上传指令

### 方法1：Google Drive（推荐）

```bash
# 1. 解压压缩包
tar -xzf florr_mob_detector_training_package.tar.gz

# 2. 上传到 Google Drive
# - 打开 https://drive.google.com/
# - 创建文件夹：florr_dataset
# - 上传 upload_package 内容
```

### 方法2：Colab 直接上传

在 Colab Notebook 中运行：

```python
# 方法A：上传压缩包
from google.colab import files
uploaded = files.upload()  # 选择 florr_mob_detector_training_package.tar.gz

# 解压
!tar -xzf florr_mob_detector_training_package.tar.gz

# 方法B：从 GitHub 克隆
!git clone https://github.com/PANP2010/florr_powerful_tools.git
!cd florr_powerful_tools && tar -xzf florr_mob_detector_training_package.tar.gz
```

---

## 🚀 恒源云上传指令

### 使用 SCP 上传

```bash
# 1. 上传压缩包到服务器
scp florr_mob_detector_training_package.tar.gz root@your-server-ip:/root/

# 2. SSH 登录服务器
ssh root@your-server-ip

# 3. 解压
cd /root
tar -xzf florr_mob_detector_training_package.tar.gz

# 4. 查看内容
ls -la upload_package/
```

### 使用 rsync 上传（更快）

```bash
# 同步整个文件夹
rsync -avz upload_package/ root@your-server-ip:/root/florr_dataset/
```

---

## 📋 快速上传命令汇总

### Kaggle
```bash
# 解压
tar -xzf florr_mob_detector_training_package.tar.gz

# API 上传
cd upload_package
kaggle datasets create -p dataset
```

### Colab
```python
# 在 Colab 中运行
from google.colab import files
files.upload()  # 上传压缩包
!tar -xzf florr_mob_detector_training_package.tar.gz
```

### 恒源云
```bash
# 上传
scp florr_mob_detector_training_package.tar.gz root@your-ip:/root/

# 解压
ssh root@your-ip "cd /root && tar -xzf florr_mob_detector_training_package.tar.gz"
```

---

## ⚠️ 重要提醒

**当前数据集只有验证集（val），缺少训练集（train）！**

您需要：

1. **准备训练数据**
   - 至少 500-1000 张训练图片
   - 对应的 YOLO 格式标签文件

2. **创建训练集目录**
   ```bash
   cd upload_package/dataset
   mkdir -p train/images train/labels
   ```

3. **添加训练数据**
   - 将图片放入 `train/images/`
   - 将标签放入 `train/labels/`

4. **更新 data.yaml**
   ```yaml
   path: /path/to/dataset
   train: train/images  # 添加这行
   val: val/images
   ```

5. **重新打包**
   ```bash
   tar -czf florr_mob_detector_training_package.tar.gz upload_package/
   ```

---

## 🎯 下一步

1. ✅ 解压压缩包
2. ⚠️ 准备训练数据集
3. ✅ 选择平台并上传
4. ✅ 运行训练脚本

详细说明请查看压缩包内的 `README.md` 文件。
