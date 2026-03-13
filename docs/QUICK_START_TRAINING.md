# YOLOv8s Mob检测器训练 - 快速开始

## 📋 准备工作

### 1. 数据集结构
确保你的数据集符合YOLO格式：
```
dataset/
├── data.yaml          # 配置文件
├── train/
│   ├── images/        # 训练图片
│   └── labels/        # 训练标签（.txt格式）
└── val/
    ├── images/        # 验证图片
    └── labels/        # 验证标签（.txt格式）
```

### 2. data.yaml配置
```yaml
path: /path/to/dataset
train: train/images
val: val/images
nc: 81  # 类别数量
names:
  0: ant_baby
  1: ant_egg
  # ... 其他类别
```

---

## 🚀 方案一：Kaggle（推荐）

### 步骤：

1. **上传数据集到Kaggle**
   - 访问 https://www.kaggle.com/datasets
   - 点击 "New Dataset"
   - 上传你的数据集文件夹
   - 设置为Private

2. **创建Notebook**
   - 访问 https://www.kaggle.com/code
   - 点击 "New Notebook"
   - 设置 Accelerator: GPU P100
   - 上传 `train_mob_detector_notebook.ipynb`

3. **添加数据集**
   - 在Notebook右侧点击 "Add Data"
   - 搜索并添加你的数据集

4. **修改路径**
   ```python
   data_yaml = '/kaggle/input/your-dataset-name/data.yaml'
   ```

5. **运行训练**
   - 点击 "Run All"
   - 等待训练完成（约2-4小时）

6. **下载模型**
   - 在Output区域下载 `best.pt`

---

## 🚀 方案二：Google Colab

### 步骤：

1. **准备数据集**
   - 上传到Google Drive
   - 或使用GitHub克隆

2. **创建Notebook**
   - 访问 https://colab.research.google.com/
   - 上传 `train_mob_detector_notebook.ipynb`
   - 设置 Runtime: GPU

3. **挂载Google Drive**
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```

4. **修改路径**
   ```python
   data_yaml = '/content/drive/MyDrive/your-dataset/data.yaml'
   ```

5. **运行训练**
   - 点击 "Run All"
   - 防止断开（见下方技巧）

6. **下载模型**
   - 自动保存到Google Drive
   - 或手动下载

### 防止Colab断开：
在浏览器控制台（F12）运行：
```javascript
function ClickConnect(){
    console.log("Clicked on connect button"); 
    document.querySelector("colab-connect-button").click()
}
setInterval(ClickConnect, 60000)
```

---

## 🚀 方案三：恒源云（低成本）

### 步骤：

1. **注册并租用GPU**
   - 访问 https://gpushare.com/
   - 租用 RTX 3090（约1-2元/小时）

2. **连接实例**
   - 使用SSH或JupyterLab

3. **上传数据集**
   ```bash
   scp -r dataset/ root@your-ip:/root/
   ```

4. **训练**
   ```bash
   python train_mob_detector_colab.py \
       --data /root/dataset/data.yaml \
       --epochs 100 \
       --batch 32
   ```

5. **下载模型**
   ```bash
   scp root@your-ip:/root/runs/mob_detector_yolov8s/weights/best.pt .
   ```

---

## 📊 训练参数建议

| 平台 | GPU | Batch Size | Epochs | 预计时间 |
|------|-----|------------|--------|----------|
| Kaggle | P100 | 16 | 100 | 3-4小时 |
| Colab | T4 | 16 | 100 | 3-4小时 |
| 恒源云 | 3090 | 32 | 100 | 1-2小时 |

---

## 🔧 常见问题

### Q: 显存不足怎么办？
A: 减小batch size（16→8→4）或图像尺寸（640→512）

### Q: 训练速度慢？
A: 确保使用GPU，检查 `torch.cuda.is_available()`

### Q: 如何使用训练好的模型？
A: 
```python
from ultralytics import YOLO
model = YOLO('best.pt')
results = model.predict('image.jpg')
results[0].show()
```

---

## 📁 文件清单

- `train_mob_detector_colab.py` - 通用训练脚本
- `train_mob_detector_notebook.ipynb` - Jupyter Notebook模板
- `data_cloud.yaml` - 云端数据集配置模板
- `FREE_GPU_TRAINING_GUIDE.md` - 详细使用指南

---

## 🎯 下一步

1. 选择平台（推荐Kaggle）
2. 准备数据集
3. 上传并配置
4. 开始训练
5. 下载模型并测试

祝训练顺利！🚀
