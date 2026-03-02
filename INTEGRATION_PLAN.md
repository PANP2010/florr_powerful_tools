# Florr Assistant - 整合工具开发规划

> 创建日期: 2026-02-21  
> 目标: 打造一个强大、美观、跨平台的florr.io自动游玩辅助工具

---

## 一、项目概述

### 1.1 产品定位

**Florr Assistant** 是一款为florr.io游戏设计的智能辅助工具，整合现有模块功能，提供：

- 🎮 **自动战斗** - 智能刷怪、自动攻击
- 🗺️ **自动寻路** - 智能导航、地图识别
- 🛡️ **AFK防护** - 自动响应验证、防踢出
- 📊 **数据统计** - 收集效率、花瓣统计
- 🎨 **美观界面** - 现代化UI设计

### 1.2 核心价值

| 维度 | 目标 | 实现方式 |
|------|------|----------|
| **功能性** | 全自动游玩 | 整合AI模型+路径规划+自动化 |
| **易用性** | 一键启动 | 统一入口、自动配置 |
| **美观性** | 现代UI | PyQt5/PySide6 + 现代设计语言 |
| **跨平台** | Win/Mac/Linux | 纯Python + 跨平台API |
| **轻量级** | 快速启动 | 模块化加载、按需启动 |

---

## 二、技术架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Florr Assistant                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    UI Layer (PyQt5)                  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │   │
│  │  │ Dashboard│ │ Settings │ │  Stats   │ │  Log   │ │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Core Services                       │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │   │
│  │  │  Engine  │ │  Config  │ │  Logger  │ │ Event  │ │   │
│  │  │ Manager  │ │ Manager  │ │ Manager  │ │ Bus    │ │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Feature Modules                    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │   │
│  │  │   AFK    │ │ Pathing  │ │  Combat  │ │ Stats  │ │   │
│  │  │  Module  │ │  Module  │ │  Module  │ │ Module │ │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Platform Layer                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │   │
│  │  │  Screen  │ │  Input   │ │  Audio   │            │   │
│  │  │ Capture  │ │ Control  │ │  Alert   │            │   │
│  │  └──────────┘ └──────────┘ └──────────┘            │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    AI Models                         │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │   │
│  │  │   YOLO   │ │  Map     │ │  Combat  │            │   │
│  │  │ Detector │ │Classifier│ │  Model   │            │   │
│  │  └──────────┘ └──────────┘ └──────────┘            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
florr_powerful_tools/
├── florr_assistant/              # 主应用目录
│   ├── __init__.py
│   ├── main.py                   # 应用入口
│   ├── app.py                    # 应用主类
│   │
│   ├── core/                     # 核心服务
│   │   ├── __init__.py
│   │   ├── engine.py             # 引擎管理器
│   │   ├── config.py             # 配置管理
│   │   ├── logger.py             # 日志管理
│   │   ├── events.py             # 事件总线
│   │   └── platform.py           # 平台适配
│   │
│   ├── ui/                       # 用户界面
│   │   ├── __init__.py
│   │   ├── main_window.py        # 主窗口
│   │   ├── dashboard.py          # 仪表盘
│   │   ├── settings.py           # 设置页面
│   │   ├── stats.py              # 统计页面
│   │   ├── styles.py             # 样式定义
│   │   └── resources/            # UI资源
│   │       ├── icons/
│   │       ├── themes/
│   │       └── fonts/
│   │
│   ├── modules/                  # 功能模块
│   │   ├── __init__.py
│   │   ├── base.py               # 模块基类
│   │   ├── afk/                  # AFK防护模块
│   │   │   ├── __init__.py
│   │   │   ├── detector.py
│   │   │   └── responder.py
│   │   ├── pathing/              # 寻路模块
│   │   │   ├── __init__.py
│   │   │   ├── navigator.py
│   │   │   └── map_classifier.py
│   │   ├── combat/               # 战斗模块
│   │   │   ├── __init__.py
│   │   │   ├── fighter.py
│   │   │   └── target_selector.py
│   │   └── stats/                # 统计模块
│   │       ├── __init__.py
│   │       └── collector.py
│   │
│   ├── platform/                 # 平台适配层
│   │   ├── __init__.py
│   │   ├── base.py               # 平台基类
│   │   ├── windows.py            # Windows实现
│   │   ├── macos.py              # macOS实现
│   │   └── linux.py              # Linux实现
│   │
│   └── models/                   # AI模型
│       ├── __init__.py
│       ├── yolo_detector.py
│       └── map_classifier.py
│
├── models/                       # 模型文件
│   ├── afk-det.pt
│   ├── afk-seg.pt
│   ├── map_classifier.pth
│   └── combat_model.pt
│
├── config/                       # 配置文件
│   ├── default.yaml
│   └── themes/
│
├── assets/                       # 资源文件
├── docs/                         # 文档
└── scripts/                      # 工具脚本
```

---

## 三、功能模块设计

### 3.1 AFK防护模块

**功能描述**: 自动检测并响应游戏AFK验证

```python
class AFKModule(BaseModule):
    features = [
        "YOLO检测AFK窗口",
        "自动点击验证按钮",
        "LLM智能对话响应",
        "WebSocket扩展集成"
    ]
    
    cross_platform = True
    priority = "critical"
```

**跨平台适配**:
- Windows: BitBlt/GDI/WGC屏幕捕获
- macOS: Quartz屏幕捕获
- Linux: X11/Wayland屏幕捕获

### 3.2 自动寻路模块

**功能描述**: 智能路径规划与自动导航

```python
class PathingModule(BaseModule):
    features = [
        "地图类型自动识别",
        "Lazy Theta*路径规划",
        "玩家位置检测",
        "防卡死机制"
    ]
    
    cross_platform = True
    priority = "high"
```

### 3.3 自动战斗模块

**功能描述**: 自动刷怪与战斗

```python
class CombatModule(BaseModule):
    features = [
        "怪物检测与追踪",
        "自动攻击",
        "装备切换",
        "沙暴规避"
    ]
    
    cross_platform = True
    priority = "high"
```

### 3.4 数据统计模块

**功能描述**: 收集效率与花瓣统计

```python
class StatsModule(BaseModule):
    features = [
        "花瓣掉落统计",
        "效率分析",
        "历史记录",
        "导出报告"
    ]
    
    cross_platform = True
    priority = "medium"
```

---

## 四、UI设计规范

### 4.1 设计原则

1. **简洁现代** - 扁平化设计，减少视觉噪音
2. **信息层次** - 重要信息突出，次要信息收敛
3. **操作便捷** - 一键操作，快捷键支持
4. **主题切换** - 支持亮色/暗色主题

### 4.2 配色方案

**亮色主题**:
```css
--primary: #4A90D9;      /* 主色调 - 蓝色 */
--secondary: #7B68EE;    /* 辅助色 - 紫色 */
--success: #4CAF50;      /* 成功 - 绿色 */
--warning: #FF9800;      /* 警告 - 橙色 */
--danger: #F44336;       /* 危险 - 红色 */
--background: #FFFFFF;   /* 背景 */
--surface: #F5F5F5;      /* 表面 */
--text: #212121;         /* 文字 */
```

**暗色主题**:
```css
--primary: #64B5F6;
--secondary: #9575CD;
--success: #81C784;
--warning: #FFB74D;
--danger: #E57373;
--background: #121212;
--surface: #1E1E1E;
--text: #FFFFFF;
```

### 4.3 界面布局

```
┌────────────────────────────────────────────────────────────┐
│  ┌──────┐  Florr Assistant                    ─ □ ×      │
│  │ 🌸   │                                                  │
│  └──────┘                                                  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                    状态面板                          │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │ │
│  │  │ AFK防护 │ │ 自动寻路 │ │ 自动战斗 │ │ 数据统计 │   │ │
│  │  │   ✅    │ │   ⏸️    │ │   ▶️    │ │   ⏹️    │   │ │
│  │  │  运行中  │ │  已暂停  │ │  运行中  │ │  已停止  │   │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────┐ ┌────────────────────────────┐ │
│  │      实时信息        │ │         日志输出           │ │
│  │                      │ │                            │ │
│  │  当前地图: Ocean     │ │  [12:00:01] AFK检测启动   │ │
│  │  运行时间: 2h 30m    │ │  [12:00:05] 地图识别完成  │ │
│  │  收集花瓣: 156       │ │  [12:01:23] 发现沙暴      │ │
│  │  效率: 62/h          │ │  [12:02:00] 自动规避完成  │ │
│  │                      │ │  ...                       │ │
│  └──────────────────────┘ └────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  [  开始全部  ]  [  停止全部  ]  [  设置  ]  [  关于 ] │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## 五、跨平台适配方案

### 5.1 屏幕捕获

```python
class ScreenCapture(ABC):
    @abstractmethod
    def capture(self, region: tuple) -> np.ndarray:
        pass

class WindowsCapture(ScreenCapture):
    def capture(self, region):
        # BitBlt / WGC
        pass

class MacOSCapture(ScreenCapture):
    def capture(self, region):
        # Quartz / mss
        pass

class LinuxCapture(ScreenCapture):
    def capture(self, region):
        # X11 / mss
        pass
```

### 5.2 输入控制

```python
class InputControl(ABC):
    @abstractmethod
    def click(self, x: int, y: int): pass
    
    @abstractmethod
    def move(self, x: int, y: int): pass
    
    @abstractmethod
    def key_press(self, key: str): pass

# 使用pyautogui作为跨平台基础
# Windows: pyautogui + pywin32增强
# macOS: pyautogui + pyobjc增强
# Linux: pyautogui + python-xlib增强
```

### 5.3 依赖管理

```txt
# requirements.txt
PyQt5>=5.15.0          # UI框架
ultralytics>=8.0.0     # YOLO模型
opencv-python>=4.8.0   # 图像处理
numpy>=1.24.0          # 数值计算
pyautogui>=0.9.54      # 跨平台输入控制
pyyaml>=6.0            # 配置文件
pillow>=10.0.0         # 图像处理

# 平台特定依赖 (可选)
pywin32>=305; sys_platform == 'win32'
pyobjc>=9.0; sys_platform == 'darwin'
python-xlib>=0.33; sys_platform == 'linux'
```

---

## 六、开发计划

### Phase 1: 基础框架 (第1-2周)

- [ ] 创建项目结构
- [ ] 实现核心服务层
- [ ] 实现平台适配层
- [ ] 基础UI框架

### Phase 2: 模块整合 (第3-4周)

- [ ] AFK模块迁移与优化
- [ ] 寻路模块迁移与优化
- [ ] 战斗模块迁移与优化
- [ ] 统计模块实现

### Phase 3: UI完善 (第5-6周)

- [ ] 主界面实现
- [ ] 设置页面实现
- [ ] 主题系统实现
- [ ] 国际化支持

### Phase 4: 测试与优化 (第7-8周)

- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能优化
- [ ] 文档完善

---

## 七、风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 游戏更新导致模型失效 | 高 | 模块化设计，快速更新模型 |
| 跨平台兼容性问题 | 中 | 充分测试，使用成熟库 |
| 性能问题 | 中 | 异步处理，资源优化 |
| 用户误操作 | 低 | 确认机制，操作日志 |

---

## 八、成功指标

1. **功能完整性**: 所有模块正常运行
2. **跨平台兼容**: Win/Mac/Linux均可使用
3. **用户体验**: 启动时间<3秒，操作简单
4. **稳定性**: 连续运行24小时无崩溃
5. **效率**: 收集效率达到手动操作的80%以上

---

*文档版本: 1.0*  
*最后更新: 2026-02-21*
