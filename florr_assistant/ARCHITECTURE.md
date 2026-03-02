# florr_assistant 项目架构文档

## 项目概述

florr_assistant 是一个用于YOLO模型检测游戏中的怪物，并做出自动化决策的AI助手工具。

## 当前状态

- **版本**: V4 (高质量训练版)
- **训练数据**: 2040张合成图片
- **怪物类别**: 77类
- **最佳mAP50**: 0.39 (Epoch 15)
- **怪物尺寸范围**: 0.08-0.5 (相对于原图)
- **训练状态**: 已完成 (17 epochs, early stopping)
- **模型文件**: 19MB (19160035 bytes)

## 训练进度

| Epoch | mAP50 | mAP50-95 | Precision | Recall |
|-------|-------|----------|-----------|--------|
| 1 | 0.03 | 0.01 | 0.04 | 0.11 |
| 5 | 0.22 | 0.14 | 0.55 | 0.18 |
| 10 | 0.37 | 0.25 | 0.73 | 0.31 |
| 15 | **0.39** | **0.28** | **0.81** | **0.32** |
| 17 | 0.28 | 0.15 | 0.73 | 0.20 |

**注意**: 训练在Epoch 17时early stopping，最终采用Epoch 15的最佳模型

## 核心模块

### 1. MapClassifier (地图分类器) ✅ 新增

**功能**: 使用多尺度模板匹配从游戏截图中识别当前地图

**输入**: 
- 游戏截图 (PNG格式, 通常2940x1912)

**输出**: 
- 地图名称 (garden, desert, ocean, hel, jungle, anthell, factory, sewers, worm's inside)
- 置信度 (0-1)
- 地图在屏幕上的位置和大小

**算法**: 
- 多尺度模板匹配 (0.5x - 2.0x)
- 金字塔搜索优化
- 搜索区域: 右上角 35%宽度 × 40%高度

**性能**:
- 置信度: 0.885 (garden测试)
- 缩放检测: 1.55x
- 模板数量: 9个地图

**使用示例**:
```python
from modules.pathing import MapClassifier, FullscreenTemplateMatcher

# 方式1: 直接使用匹配器
matcher = FullscreenTemplateMatcher('./resources/maps')
result = matcher.match(screenshot, threshold=0.4)
print(f"地图: {result.map_name}, 置信度: {result.confidence}")

# 方式2: 使用模块
classifier = MapClassifier({'confidence_threshold': 0.4})
result = classifier.classify(screenshot)
print(f"地图: {result['map']}")
```

### 2. MobDetector (怪物检测器)

**功能**: 使用YOLOv8模型检测游戏画面中的怪物

**输入**: 
- 游戏截图 (PNG格式, 通常2940x1912)

**输出**: 
- 检测到的怪物列表
- 每个怪物包含: 类别名、置信度、边界框坐标

**模型**: 
- 路径: `data/runs/mob_detector_v4/weights/best.pt`
- 架构: YOLOv8n (nano版本)
- 输入尺寸: 640x640
- 置信度阈值: 0.25

**训练数据**:
- 来源: 合成数据 (无背景怪物图像 + 游戏背景)
- 数量: 2040张 (训练1734张, 验证306张)
- 每张背景生成60个样本
- 怪物数量: 5-20个/图
- 怪物尺寸: 0.08-0.5 (相对于原图)
- 数据增强: 旋转0-360度, 亮度调整30%概率

**性能**:
- mAP50: 0.39
- mAP50-95: 0.28
- 推理速度: ~36ms/图 (MPS)

### 2. DataCollector (数据收集器)

**功能**: 收集游戏截图和操作数据

**输入**: 
- 游戏窗口截图
- 键盘/鼠标操作

**输出**: 
- JSONL格式数据文件
- 包含: 时间戳、截图路径、操作记录

**文件路径**: `data/collected_data/`

### 3. StateEncoder (状态编码器)

**功能**: 将游戏状态编码为模型可理解的格式

**输入**: 
- 检测到的怪物列表
- 玩家状态 (血量、角度、阴阳)

**输出**: 
- 73维状态向量
  - health: 1维 (0-1归一化)
  - degree: 1维 (花瓣旋转角度)
  - yinyang: 1维 (阴阳状态)
  - mobs: 70维 (10个怪物 × 7特征)
    - 每个怪物: x, y, width, height, 3类one-hot编码

**参考**: `florr-auto-framework-pytorch/dataset_utils.py`

### 4. FlorrModel (决策模型)

**功能**: 根据状态做出移动/攻击/防御决策

**输入**: 
- 73维状态向量

**输出**: 
- 5维动作向量
  - move_x: 移动X方向 (-1到1)
  - move_y: 移动Y方向 (-1到1)
  - attack: 攻击 (0或1)
  - defend: 防御 (0或1)
  - yinyang: 阴阳切换 (0或1)

**架构**: 
```
FlorrModel(
  fc1: Linear(73, 128)
  relu1: ReLU()
  fc2: Linear(128, 64)
  relu2: ReLU()
  fc3: Linear(64, 5)
  tanh: Tanh()  # move输出
  sigmoid: Sigmoid()  # attack/defend/yinyang输出
)
```

**参考**: `florr-auto-framework-pytorch` 原项目

## 数据流程
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  游戏截图   │ --> │ MapClassifier│ --> │  MobDetector │ --> │ StateEncoder │
│  (2940x1912)│     │ (模板匹配)   │     │  (YOLOv8n)   │     │  (73维向量)  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                                       │
                           v                                       v
                    ┌─────────────┐                         ┌─────────────┐
                    │ 地图识别结果 │                         │ FlorrModel  │
                    │ 地图名称/位置│                         │  (MLP决策)  │
                    └─────────────┘                         └─────────────┘
```

## 训练记录

| 版本 | 数据量 | 怪物尺寸 | mAP50 | mAP50-95 | 状态 |
|------|--------|----------|-------|----------|------|
| V1 | 1360张 | 0.2-1.2 | 0.48 | 0.30 | 已完成 |
| V2 | 1360张 | 0.1-0.6 | 0.72 | 0.47 | 已完成 |
| V3 | 1360张 | 0.1-0.6 | 0.13 | 0.09 | 效果差 |
| **V4** | **2040张** | **0.08-0.5** | **0.39** | **0.28** | **已完成** |

## 文件结构
```
florr_powerful_tools/
├── florr_assistant/
│   ├── __init__.py
│   ├── ARCHITECTURE.md              # 本文档
│   ├── mob_detector.py              # 怪物检测器
│   ├── data_collector_tool.py       # 数据收集工具
│   ├── generate_high_quality_data.py # 数据生成器V4
│   ├── generate_synthetic_data_v3.py # 数据生成器V3
│   ├── train_mob_detector_v4.py     # 训练脚本V4
│   ├── train_mob_detector_mps.py    # MPS加速训练
│   ├── test_trained_model.py        # 测试脚本
│   ├── test_image2.py               # 测试图2
│   ├── test_image3.py               # 测试图3
│   │
│   ├── resources/                   # 资源文件 ✅ 新增
│   │   └── maps/                    # 地图模板 (9个)
│   │       ├── anthell.png          # 蚂蚁地狱
│   │       ├── desert.png           # 沙漠
│   │       ├── factory.png          # 工厂
│   │       ├── garden.png           # 花园
│   │       ├── hel.png              # 地狱
│   │       ├── jungle.png           # 丛林
│   │       ├── ocean.png            # 海洋
│   │       ├── sewers.png           # 下水道
│   │       └── worm's inside.png    # 虫子内部
│   │
│   └── modules/
│       └── pathing/
│           ├── map_classifier.py    # 地图分类器 ✅ 新增
│           └── navigator.py         # 导航器
│
├── data/
│   ├── synthetic_mobs_v4/           # V4合成数据集
│   │   ├── data.yaml                # YOLO配置
│   │   ├── classes.txt              # 类别列表(77类)
│   │   ├── images/
│   │   │   ├── train/               # 训练图片(1734张)
│   │   │   └── val/                 # 验证图片(306张)
│   │   └── labels/
│   │       ├── train/               # 训练标注
│   │       └── val/                 # 验证标注
│   │
│   ├── runs/
│   │   ├── mob_detector_v4/         # V4训练结果
│   │   │   ├── weights/
│   │   │   │   ├── best.pt          # 最佳模型(19MB)
│   │   │   │   └── last.pt          # 最新模型
│   │   │   ├── results.csv          # 训练指标
│   │   │   └── labels.jpg           # 标签分布图
│   │   │
│   │   ├── mob_detector_v3_mps/     # V3训练结果
│   │   └── mob_detector_v3_mps3/    # V3优化训练结果
│   │
│   └── [背景图片]                    # 游戏背景图
│       ├── g.png - g6.png           # 花园(Garden)
│       ├── ah.png - ah5.png         # 蚂蚁地狱(Ant Hell)
│       ├── d.png - d4.png           # 沙漠(Desert)
│       ├── f.png - f4.png           # 丛林(Jungle)
│       ├── h.png                    # 地狱(Hel)
│       ├── o1.png - o5.png          # 海洋(Ocean)
│       └── s.png - s3.png           # 下水道(Sewer)
│
└── florr-auto-framework-pytorch/
    ├── mob检测测试图.png             # 测试图1
    ├── mob检测测试图_结果.png        # 测试结果1(V3)
    ├── mob检测测试图_结果_v4.png      # V4测试结果1
    ├── 测试图2.png                   # 测试图2
    ├── 测试图2_结果.png              # 测试结果2(V3)
    ├── 测试图2_结果_v4.png            # V4测试结果2
    ├── 测试图3.png                   # 测试图3
    └── 测试图3_结果.png              # 测试结果3(V3)
```

## 怪物类别 (77类)

### 花园 (Garden)
ladybug, bee, beetle, ant_baby, ant_worker, ant_soldier, centipede, fly, bumble_bee, hornet, mantis, spider

### 蚂蚁地狱 (Ant Hell)
ant_baby, ant_worker, ant_soldier, ant_queen, ant_egg, ant_hole, fire_ant_baby, fire_ant_worker, fire_ant_soldier

### 沙漠 (Desert)
beetle_mummy, beetle_pharaoh, beetle_nazar, scorpion, centipede_desert, sandstorm, digger, firefly, firefly_magic

### 丛林 (Jungle)
centipede, centipede_body, mantis, leafbug, leafbug_shiny, spider, hornet, wasp, beetle

### 地狱 (Hel)
beetle_hel, centipede_hel, centipede_hel_body, spider_hel, wasp_hel, leech, leech_body, moth

### 海洋 (Ocean)
jellyfish, bubble, crab, crab_mecha, starfish, sponge, shell, worm

### 下水道 (Sewer)
roach, fly, centipede, spider, beetle, worm, worm_guts

## 使用方法

### 1. 怪物检测
```python
from ultralytics import YOLO
import cv2

model = YOLO('data/runs/mob_detector_v4/weights/best.pt')
image = cv2.imread('game_screenshot.png')

results = model(image, imgsz=640, conf=0.25)

for result in results:
    boxes = result.boxes
    for box in boxes:
        class_name = result.names[int(box.cls[0])]
        confidence = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        print(f"{class_name}: {confidence:.2f} at ({x1:.0f}, {y1:.0f})")
```

### 2. 数据生成
```bash
python florr_assistant/generate_high_quality_data.py
```

### 3. 模型训练
```bash
python florr_assistant/train_mob_detector_v4.py
```

### 4. 测试验证
```bash
python florr_assistant/test_trained_model.py
```

## 已知问题

1. **Domain Gap**: 合成数据与真实游戏场景存在差异
2. **小目标检测**: 小尺寸怪物检测效果不佳
3. **误检**: 存在将背景误检为怪物的情况
4. **漏检**: 部分怪物检测数量不足

## 改进方向

1. **收集真实数据**: 使用DataCollector收集真实游戏截图
2. **手动标注**: 对真实数据进行标注
3. **混合训练**: 合成数据 + 真实数据混合训练
4. **模型优化**: 尝试更大的YOLO模型 (YOLOv8s/m)
5. **数据增强**: 增加更多变换方式

## 参考项目

- [florr-auto-framework-pytorch](https://github.com/Shiny-Ladybug/florr-auto-framework-pytorch) - 原项目参考
