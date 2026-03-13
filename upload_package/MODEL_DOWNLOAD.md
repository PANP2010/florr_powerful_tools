# YOLO26s 模型下载说明

## ⚠️ 重要说明

由于本地 SSL 证书问题，无法直接下载 YOLO26s 模型文件。但是，**您不需要手动下载**！

## 🎯 推荐方案：云端自动下载

在 Kaggle、Colab 或恒源云上运行训练脚本时，Ultralytics 会**自动下载** YOLO26s 模型文件。

### Kaggle/Colab

```python
# 安装 Ultralytics
!pip install -q ultralytics

# 第一次运行时会自动下载 yolo26s.pt
from ultralytics import YOLO
model = YOLO('yolo26s.pt')  # 自动下载
```

### 恒源云

```bash
pip install ultralytics
python -c "from ultralytics import YOLO; YOLO('yolo26s.pt')"  # 自动下载
```

## 📥 手动下载（可选）

如果您想提前下载模型文件：

### 方法1：GitHub Releases

1. 访问 https://github.com/ultralytics/assets/releases
2. 找到最新版本（v26.0.0 或更高）
3. 下载 `yolo26s.pt` 文件
4. 放到 `upload_package/` 目录

### 方法2：使用 wget（Linux/macOS）

```bash
# 忽略 SSL 证书下载
wget --no-check-certificate -O yolo26s.pt https://github.com/ultralytics/assets/releases/download/v26.0.0/yolo26s.pt
```

### 方法3：使用 curl

```bash
curl -k -L -o yolo26s.pt https://github.com/ultralytics/assets/releases/download/v26.0.0/yolo26s.pt
```

## 🔧 训练脚本已优化

训练脚本 `train_cloud.py` 已经优化，会自动处理模型下载：

```python
# 方式1：自动下载（推荐）
model = YOLO('yolo26s.pt')

# 方式2：使用本地文件（如果已下载）
model = YOLO('./yolo26s.pt')
```

## 📊 模型信息

| 模型 | 文件名 | 大小 | mAP50-95 | 参数量 |
|------|--------|------|----------|--------|
| YOLO26s | yolo26s.pt | ~22MB | 48.6% | 9.5M |

## ✅ 验证下载

下载完成后，可以验证模型：

```python
from ultralytics import YOLO

model = YOLO('yolo26s.pt')
print(f"模型加载成功: {model.model_name}")
print(f"参数量: {sum(p.numel() for p in model.model.parameters()) / 1e6:.2f}M")
```

## 🚀 开始训练

无需担心模型文件，直接运行训练脚本即可：

```bash
python scripts/train_cloud.py --mode all --num-samples 5000
```

首次运行时会自动下载模型文件（约 22MB）。

---

**提示**: 云端平台（Kaggle/Colab）的网络环境通常更好，自动下载会更快更稳定。
