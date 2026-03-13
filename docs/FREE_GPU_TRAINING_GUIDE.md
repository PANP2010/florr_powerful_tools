# 免费GPU训练平台使用指南

本文档介绍如何使用免费GPU平台训练YOLOv8s Mob检测器模型。

## 平台对比

| 平台 | GPU型号 | 显存 | 时长限制 | 优点 | 缺点 |
|------|---------|------|----------|------|------|
| **Google Colab** | T4/P100 | 15GB | 12小时/次 | 易用性好，灵活性高 | 时长限制，可能断开 |
| **Kaggle Kernels** | P100/T4 | 13GB | 30小时/周 | 时长更长，稳定性好 | 需要上传数据集 |
| **恒源云** | 3090/4090 | 24GB+ | 按量付费 | 性能强，无限制 | 需要付费（便宜） |

**推荐顺序**: Kaggle > Google Colab > 恒源云（付费）

---

## 方案一：Kaggle Kernels（推荐）

### 1. 准备数据集

#### 方法A：上传到Kaggle Dataset
1. 访问 https://www.kaggle.com/datasets
2. 点击 "New Dataset"
3. 上传你的数据集文件夹（包含 `data.yaml` 和图像/标签）
4. 设置为Private或Public

#### 方法B：使用Kaggle API上传
```bash
# 安装 Kaggle API
pip install kaggle

# 配置 API Key（从 https://www.kaggle.com/settings 获取）
mkdir -p ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# 创建数据集
kaggle datasets create -p /path/to/your/dataset
```

### 2. 创建Notebook

1. 访问 https://www.kaggle.com/code
2. 点击 "New Notebook"
3. 在右侧设置中：
   - Accelerator: GPU P100 或 T4
   - Language: Python
   - Environment: 最新的Python环境

### 3. 添加数据集

在Notebook中：
1. 点击右侧 "Add Data"
2. 搜索并添加你上传的数据集
3. 数据会被挂载到 `/kaggle/input/你的数据集名称/`

### 4. 训练代码

```python
# 安装依赖
!pip install ultralytics

# 导入训练脚本
import sys
sys.path.append('/kaggle/input/your-code-folder')

# 或者直接在Notebook中运行
from ultralytics import YOLO

# 加载模型
model = YOLO('yolov8s.pt')

# 训练
results = model.train(
    data='/kaggle/input/your-dataset/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='mob_detector_yolov8s',
    project='/kaggle/working/runs',
    device='cuda',
    patience=20,
    save=True,
    plots=True,
)

# 保存模型
import shutil
shutil.make_archive('/kaggle/working/mob_detector_model', 'zip', 
                    '/kaggle/working/runs/mob_detector_yolov8s')
```

### 5. 下载模型

训练完成后，在右侧 "Output" 区域下载生成的模型文件。

---

## 方案二：Google Colab

### 1. 创建Notebook

1. 访问 https://colab.research.google.com/
2. 创建新的Notebook
3. 在菜单中选择: Runtime > Change runtime type > GPU

### 2. 挂载Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

### 3. 上传数据集

#### 方法A：上传到Google Drive
```python
# 数据集路径
data_path = '/content/drive/MyDrive/florr_dataset/data.yaml'
```

#### 方法B：从GitHub克隆
```python
!git clone https://github.com/PANP2010/florr_powerful_tools.git
data_path = '/content/florr_powerful_tools/data/data.yaml'
```

### 4. 训练代码

```python
# 安装依赖
!pip install ultralytics

from ultralytics import YOLO

# 加载模型
model = YOLO('yolov8s.pt')

# 训练
results = model.train(
    data=data_path,
    epochs=100,
    imgsz=640,
    batch=16,
    name='mob_detector_yolov8s',
    project='/content/drive/MyDrive/models',
    device='cuda',
    patience=20,
    save=True,
    plots=True,
)

# 复制模型到Google Drive
!cp -r runs/mob_detector_yolov8s /content/drive/MyDrive/models/
```

### 5. 防止断开连接

Colab可能会因为不活动而断开连接。在浏览器控制台运行：

```javascript
function ClickConnect(){
    console.log("Clicked on connect button"); 
    document.querySelector("colab-connect-button").click()
}
setInterval(ClickConnect, 60000)
```

---

## 方案三：恒源云（低成本付费方案）

如果免费平台无法满足需求，可以考虑恒源云：

### 1. 注册账号
访问 https://gpushare.com/ 注册账号

### 2. 租用GPU
- 选择 RTX 3090 或 RTX 4090
- 价格约 1-2 元/小时
- 无时长限制

### 3. 连接实例
```bash
# SSH连接
ssh root@your-instance-ip

# 或使用JupyterLab界面
```

### 4. 训练
```bash
# 上传数据集和代码
scp -r your_dataset root@your-instance-ip:/root/

# SSH登录后训练
python train_mob_detector_colab.py --data /root/your_dataset/data.yaml
```

---

## 训练参数建议

### YOLOv8s vs YOLOv8n

| 参数 | YOLOv8n | YOLOv8s | 说明 |
|------|---------|---------|------|
| 参数量 | 3.2M | 11.2M | s模型大3.5倍 |
| 模型大小 | 6.3MB | 22MB | s模型大3.5倍 |
| mAP | 基准 | +2-3% | s模型精度更高 |
| 速度 | 快 | 中等 | s模型稍慢 |
| 显存需求 | 4GB | 8GB | s模型需要更多显存 |

### 推荐配置

**Kaggle (P100 16GB)**
```python
batch = 16  # 或 32
imgsz = 640
epochs = 100
```

**Colab (T4 15GB)**
```python
batch = 16
imgsz = 640
epochs = 100
```

**恒源云 (3090 24GB)**
```python
batch = 32
imgsz = 640
epochs = 100
```

---

## 常见问题

### 1. 显存不足
- 减小 batch size（16 -> 8 -> 4）
- 减小图像尺寸（640 -> 512）
- 使用梯度累积

### 2. 训练速度慢
- 确保使用GPU（检查 `torch.cuda.is_available()`）
- 增加 workers 数量（4 -> 8）
- 使用混合精度训练（amp=True）

### 3. 模型下载失败
- 使用镜像源下载预训练模型
- 手动下载后上传到平台

### 4. 数据集路径错误
- 检查 data.yaml 中的路径
- 使用绝对路径
- 确保数据集结构正确

---

## 模型使用

训练完成后，将 `best.pt` 文件下载到本地：

```python
from ultralytics import YOLO

# 加载训练好的模型
model = YOLO('best.pt')

# 预测
results = model.predict('image.jpg')

# 显示结果
results[0].show()
```

---

## 下一步

1. 准备数据集（确保格式正确）
2. 选择平台（推荐 Kaggle）
3. 上传数据集和代码
4. 开始训练
5. 下载模型并测试

祝训练顺利！🚀
