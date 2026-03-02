# Florr Powerful Tools

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL%20v3-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)]()

> 一套强大的 florr.io 游戏自动化工具集合，整合AI检测、智能寻路、自动战斗等功能

---

## 项目简介

Florr Powerful Tools 是针对 [florr.io](https://florr.io) 游戏开发的自动化辅助工具集，采用计算机视觉、深度学习和路径规划算法，实现游戏内智能操作。

### 核心功能

| 功能模块 | 描述 | 状态 |
|---------|------|------|
| 🛡️ **AFK防护** | 自动检测并响应游戏AFK验证 | ✅ 可用 |
| 🗺️ **自动寻路** | 智能路径规划与自动导航 | ✅ 可用 |
| ⚔️ **自动战斗** | 自动刷怪与战斗决策 | ✅ 可用 |
| 🧠 **AI训练框架** | 自定义模型训练与部署 | ✅ 可用 |
| 📊 **数据统计** | 收集效率与花瓣统计 | ✅ 可用 |

---

## 项目结构

```
florr_powerful_tools/
├── florr_assistant/          # 整合工具主应用
│   ├── core/                 # 核心服务层
│   ├── ui/                   # 用户界面
│   └── modules/              # 功能模块
│       ├── afk/              # AFK防护模块
│       ├── pathing/          # 自动寻路模块
│       ├── combat/           # 自动战斗模块
│       └── stats/            # 数据统计模块
│
├── florr-auto-afk-main/      # AFK检测模块
├── florr-auto-pathing/       # 自动寻路模块
├── florr-auto-framework-pytorch/  # AI训练框架
├── florr-auto-sszone/        # 自动刷怪模块
├── overlay/                  # 游戏悬浮UI
├── assets/                   # 资源文件
├── config/                   # 配置文件
└── docs/                     # 文档
```

---

## 快速开始

### 环境要求

- Python 3.9 - 3.11
- 操作系统：Windows 10/11（推荐）、macOS、Linux

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/PANP2010/florr_powerful_tools.git
cd florr_powerful_tools

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r florr_assistant/requirements.txt
```

### 运行整合工具

```bash
cd florr_assistant
python main.py
```

### 运行独立模块

```bash
# AFK防护模块
cd florr-auto-afk-main
pip install -r py311-requirements.txt
python segment.py

# 自动寻路模块
cd florr-auto-pathing
python main.py

# AI训练框架
cd florr-auto-framework-pytorch
python train.py
```

---

## 功能详解

### 1. AFK防护模块 (florr-auto-afk)

自动检测并响应游戏AFK验证，防止被踢出游戏。

**核心特性：**
- YOLO模型检测AFK窗口（精度 >90%）
- 自动路径规划完成验证
- LLM智能对话响应
- WebSocket浏览器扩展集成

**技术实现：**
- 检测模型：`afk-det.pt`（3类：AFK_Window, Start, End）
- 分割模型：`afk-seg.pt`
- 路径算法：改进的Dijkstra算法

### 2. 自动寻路模块

基于地图数据的智能路径规划与自动导航。

**核心特性：**
- Lazy Theta* 路径规划算法
- 地图类型自动识别
- 玩家位置检测
- 防卡死机制

**支持地图：**
- Ocean（海洋）
- Desert（沙漠）
- Jungle（丛林）
- Garden（花园）
- Hel（地狱）
- Anthell（蚁穴）
- Sewers（下水道）

### 3. 自动战斗模块

自动刷怪与智能战斗决策。

**核心特性：**
- 怪物检测与追踪
- 自动攻击与防御
- 装备自动切换
- 沙暴检测与规避

**稀有度权重：**
| 稀有度 | 权重 |
|-------|------|
| Mythic | 3.7 |
| Ultra | 1.8 |
| Legendary | 0.6 |

### 4. AI训练框架

自定义AI模型训练与部署框架。

**神经网络架构：**
- 基础模型：3层全连接网络
- Attention增强模型：多头注意力机制
- 输入维度：73（状态特征）
- 输出维度：5（动作空间）

**训练配置：**
```python
# 自定义损失函数
loss = move_weight * move_loss + action_weight * (
    attack_loss + defend_loss + yinyang_loss
)
```

---

## 配置说明

### 主配置文件 (config/default.yaml)

```yaml
modules:
  afk:
    enabled: true
    idle_threshold: 10
    detection_interval: 3
  
  pathing:
    enabled: true
    map_classifier: "./models/map_classifier.pth"
  
  combat:
    enabled: false
    safe_distance: 200
    attack_distance: 150

ui:
  theme: "dark"  # light / dark
  language: "zh-cn"  # en-us / zh-cn
```

### AFK模块配置 (florr-auto-afk-main/config.json)

```json
{
  "runs": {
    "autoTakeOverWhenIdle": false,
    "moveAfterAFK": true,
    "idleTimeThreshold": 10
  },
  "extensions": {
    "enable": true,
    "host": "0.0.0.0",
    "port": 8000
  }
}
```

---

## 浏览器扩展

### 安装步骤

1. 安装 [Tampermonkey](https://www.tampermonkey.net/) 浏览器扩展
2. 打开 Tampermonkey 管理面板
3. 创建新脚本，粘贴 `florr-auto-afk-main/extension.js` 内容
4. 保存并启用脚本

### 功能

- 实时获取游戏数据（生命值、位置、聊天消息）
- Canvas方法拦截
- WebSocket双向通信

---

## LLM集成

支持本地和云端大语言模型进行智能对话响应。

### Ollama（本地）

```bash
# 安装 Ollama
# 访问 https://ollama.com/download

# 下载模型
ollama pull qwen3:14b

# 运行模型
ollama run qwen3:14b
```

### OpenAI API

在 `config.json` 中配置：

```json
{
  "extensions": {
    "autoChat": {
      "enable": true,
      "chatType": "openai",
      "chatEndpoint": "https://api.openai.com/v1/chat/completions",
      "chatModel": "gpt-4"
    }
  }
}
```

---

## 性能指标

| 指标 | 数值 | 说明 |
|-----|------|-----|
| AFK检测精度 | >90% | 窗口识别准确率 |
| 检测延迟 | <100ms | 从捕获到识别 |
| 路径规划时间 | <500ms | Dijkstra算法执行 |
| 整体响应时间 | <1s | 从检测到完成 |
| 推理速度 | >30 FPS | 实时推理帧率 |

---

## 技术栈

| 类别 | 技术 |
|-----|------|
| 编程语言 | Python 3.9+ |
| 计算机视觉 | OpenCV, PIL |
| 深度学习 | PyTorch, Ultralytics (YOLO) |
| GUI框架 | PyQt5, Tkinter |
| Web框架 | FastAPI, WebSocket |
| 自动化 | PyAutoGUI, PyWin32 |
| 数据处理 | NumPy, SciPy |

---

## 常见问题

### Q: 为什么GUI加载缓慢？

A: 首次启动需要加载AI模型，通常需要10秒左右。请耐心等待。

### Q: macOS上部分功能不可用？

A: 部分Windows专用API（如BitBlt、GDI）在macOS不可用。建议使用跨平台的mss库进行屏幕捕获。

### Q: 如何提高检测精度？

A: 
1. 确保游戏窗口分辨率正确（推荐1920x1080）
2. 关闭浏览器硬件加速
3. 在Chrome中禁用 `CalculateNativeWinOcclusion`

### Q: 模型文件在哪里？

A: 模型文件位于各模块的 `models/` 目录下：
- `florr-auto-afk-main/models/afk-det.pt`
- `florr-auto-afk-main/models/afk-seg.pt`

---

## 开发指南

### 添加新模块

1. 在 `florr_assistant/modules/` 创建模块目录
2. 继承 `BaseModule` 类
3. 实现必要的方法
4. 在配置文件中注册模块

```python
from florr_assistant.modules.base import BaseModule

class MyModule(BaseModule):
    def __init__(self, config):
        super().__init__(config)
        self.name = "my_module"
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def update(self):
        pass
```

### 运行测试

```bash
pytest tests/
```

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 许可证

本项目采用 GPL v3 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 致谢

- [Shiny-Ladybug](https://github.com/Shiny-Ladybug) - 原始 florr-auto-afk 项目
- [Ultralytics](https://github.com/ultralytics/ultralytics) - YOLOv8 框架

---

*最后更新: 2026-02-21*
