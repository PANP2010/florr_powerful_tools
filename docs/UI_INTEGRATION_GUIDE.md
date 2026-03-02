# UI 与游戏功能集成指南

本文档说明如何将游戏悬浮 UI 与 florr-auto-pathing 功能集成。

## 功能集成状态

| 功能 | 状态 | 说明 |
|------|------|------|
| 寻路 | ✅ 已集成 | 自动寻路到目标位置 |
| 地图识别 | ✅ 已集成 | 识别当前游戏地图 |
| 自动攻击 | ⚠️ 待实现 | 自动攻击怪物 |
| 自动防御 | ⚠️ 待实现 | 自动防御技能 |
| 阴阳切换 | ✅ 已实现 | 切换阴阳花瓣 |
| 停止 | ✅ 已实现 | 停止所有操作 |

## 已实现的功能

### 1. 寻路功能

点击"寻路"按钮后，UI 会：

1. 检测游戏状态
2. 识别当前地图
3. 获取玩家位置
4. 应用对应的地图配置
5. 执行 Lazy Theta* 寻路算法
6. 自动移动到目标位置

**使用方法**：
```python
# 在 game_overlay_ui.py 中已实现
def on_action_clicked(self, action_id):
    if action_id == "pathing":
        # 1. 检查游戏状态
        stage = check_stage()
        if stage != "in_game":
            self.update_status(f"游戏状态: {stage}")
            return
        
        # 2. 获取玩家位置
        pos = get_player_position()
        if pos is None:
            self.update_status("无法获取玩家位置")
            return
        
        # 3. 识别地图
        class_name, conf = predict_from_screenshot()
        self.update_status(f"当前地图: {class_name} (置信度: {conf:.1%})")
        
        # 4. 应用地图
        apply_map(class_name)
        
        # 5. 执行寻路
        location = (100, 100)  # 可修改为目标位置
        dedicated_area = []  # 可修改为限制区域
        
        result = lazy_theta_pathing(location, dedicated_area)
        
        # 6. 更新状态
        if result:
            self.update_status("寻路完成！")
        else:
            self.update_status("寻路失败")
```

**自定义目标位置**：

在 `game_overlay_ui.py` 中修改：

```python
# 找到这一行
location = (100, 100)

# 修改为你想要的目标位置
location = (150, 200)  # 示例：移动到 (150, 200)
```

**设置限制区域**：

```python
# 找到这一行
dedicated_area = []

# 修改为你想要的区域
dedicated_area = [(0, 0), (200, 200)]  # 示例：限制在 (0,0) 到 (200,200) 区域内
```

### 2. 地图识别功能

点击"地图识别"按钮后，UI 会：

1. 截取游戏地图区域
2. 使用训练好的 CNN 模型识别地图
3. 显示识别结果和置信度

**使用方法**：
```python
# 在 game_overlay_ui.py 中已实现
def on_action_clicked(self, action_id):
    elif action_id == "map_detect":
        try:
            self.map_detect_active = True
            self.update_status("正在识别地图...")
            
            # 1. 截图并识别
            class_name, conf = predict_from_screenshot()
            
            # 2. 更新状态
            self.map_detect_active = False
            self.update_status(f"识别结果: {class_name} (置信度: {conf:.1%})")
            
        except Exception as e:
            self.map_detect_active = False
            self.update_status(f"识别错误: {str(e)}")
```

**支持的地图**：
- anthell (蚁穴)
- desert (沙漠)
- ocean (海洋)
- hel (Hel)
- jungle (丛林)

### 3. 阴阳切换功能

点击"阴阳切换"按钮后，UI 会：

1. 模拟按下 '2' 键
2. 切换阴阳花瓣模式

**使用方法**：
```python
# 在 game_overlay_ui.py 中已实现
def on_action_clicked(self, action_id):
    elif action_id == "yinyang":
        try:
            import pyautogui
            pyautogui.press('2')
            self.update_status("已切换阴阳模式")
        except:
            self.update_status("切换失败")
```

### 4. 停止功能

点击"停止"按钮后，UI 会：

1. 停止所有正在运行的操作
2. 重置所有状态标志
3. 显示"所有操作已停止"消息

**使用方法**：
```python
# 在 game_overlay_ui.py 中已实现
def on_action_clicked(self, action_id):
    elif action_id == "stop":
        self.pathing_active = False
        self.map_detect_active = False
        self.auto_attack_active = False
        self.auto_defend_active = False
        self.update_status("所有操作已停止")
```

## 待实现的功能

### 1. 自动攻击功能

**功能描述**：
- 自动点击鼠标左键进行攻击
- 可开启/关闭
- 按钮状态显示激活状态

**实现步骤**：

1. 创建攻击线程
2. 定时触发鼠标点击
3. 更新按钮状态

**示例实现**：

```python
# 在 game_overlay_ui.py 的 __init__ 中添加
self.attack_thread = None
self.attack_timer = None

# 在 on_action_clicked 中添加
elif action_id == "auto_attack":
    self.auto_attack_active = not self.auto_attack_active
    
    if self.auto_attack_active:
        self.start_auto_attack()
    else:
        self.stop_auto_attack()
    
    status = "自动攻击: 开启" if self.auto_attack_active else "自动攻击: 关闭"
    self.update_status(status)
    self.update_button_styles()

# 添加新方法
def start_auto_attack(self):
    if self.attack_thread is None:
        self.attack_thread = AutoAttackThread()
        self.attack_thread.start()
        self.update_status("自动攻击已启动")

def stop_auto_attack(self):
    if self.attack_thread is not None:
        self.attack_thread.stop()
        self.attack_thread = None
        self.update_status("自动攻击已停止")

# 创建攻击线程类
class AutoAttackThread(QThread):
    def __init__(self):
        super().__init__()
        self.running = False
    
    def run(self):
        import pyautogui
        self.running = True
        while self.running:
            pyautogui.mouseDown(button='left')
            time.sleep(0.1)
            pyautogui.mouseUp(button='left')
            time.sleep(0.5)
    
    def stop(self):
        self.running = False
        self.wait()
```

### 2. 自动防御功能

**功能描述**：
- 自动点击鼠标右键进行防御
- 可开启/关闭
- 按钮状态显示激活状态

**实现步骤**：

与自动攻击类似，创建防御线程：

```python
# 在 game_overlay_ui.py 的 __init__ 中添加
self.defend_thread = None

# 在 on_action_clicked 中添加
elif action_id == "auto_defend":
    self.auto_defend_active = not self.auto_defend_active
    
    if self.auto_defend_active:
        self.start_auto_defend()
    else:
        self.stop_auto_defend()
    
    status = "自动防御: 开启" if self.auto_defend_active else "自动防御: 关闭"
    self.update_status(status)
    self.update_button_styles()

# 添加新方法
def start_auto_defend(self):
    if self.defend_thread is None:
        self.defend_thread = AutoDefendThread()
        self.defend_thread.start()
        self.update_status("自动防御已启动")

def stop_auto_defend(self):
    if self.defend_thread is not None:
        self.defend_thread.stop()
        self.defend_thread = None
        self.update_status("自动防御已停止")

# 创建防御线程类
class AutoDefendThread(QThread):
    def __init__(self):
        super().__init__()
        self.running = False
    
    def run(self):
        import pyautogui
        self.running = True
        while self.running:
            pyautogui.mouseDown(button='right')
            time.sleep(0.1)
            pyautogui.mouseUp(button='right')
            time.sleep(2.0)  # 防御冷却时间
    
    def stop(self):
        self.running = False
        self.wait()
```

## UI 状态显示

UI 现在包含一个"状态"面板，实时显示：

- 当前操作状态
- 错误消息
- 功能执行结果

**状态更新方法**：

```python
def update_status(self, message):
    self.status_label.setText(message)
    print(f"[状态] {message}")
```

**状态示例**：
- "就绪" - 等待操作
- "正在寻路..." - 执行寻路中
- "当前地图: desert (置信度: 98.5%)" - 地图识别结果
- "寻路完成！" - 寻路成功
- "寻路失败" - 寻路失败
- "所有操作已停止" - 停止所有功能

## 按钮状态指示

激活的功能按钮会显示不同的样式：

**未激活状态**：
- 蓝色背景：`rgba(70, 130, 180, 180)`
- 悬停时：`rgba(100, 150, 200, 220)`
- 按下时：`rgba(50, 100, 150, 200)`

**激活状态**：
- 红色背景：`rgba(180, 70, 70, 220)`
- 边框：`2px solid rgba(255, 200, 200, 255)`
- 悬停时：`rgba(200, 90, 90, 240)`

**状态更新**：

```python
def update_button_styles(self):
    for btn in self.findChildren(QPushButton):
        action_id = btn.property("action_id")
        if action_id:
            is_active = False
            if action_id == "pathing":
                is_active = self.pathing_active
            elif action_id == "map_detect":
                is_active = self.map_detect_active
            elif action_id == "auto_attack":
                is_active = self.auto_attack_active
            elif action_id == "auto_defend":
                is_active = self.auto_defend_active
            
            btn.setStyleSheet(self.get_button_style(action_id, is_active))
```

## 配置和自定义

### 修改目标位置

编辑 `game_overlay_ui.py`，找到 `on_action_clicked` 方法中的寻路部分：

```python
# 默认目标位置
location = (100, 100)

# 修改为你想要的位置
location = (150, 200)  # 示例
```

### 添加更多地图支持

如果需要支持更多地图：

1. 收集新地图的截图数据
2. 训练新的地图分类模型
3. 在 `florr-auto-pathing/utils.py` 中添加地图配置

**示例**：

```python
# 在 utils.py 的 check_map_border 中添加
def check_map_border(opencv_img):
    if MAP == "your_new_map":
        target_color = "your_color_hex"  # 地图边界颜色
        # ... 处理逻辑
```

### 自定义 UI 样式

所有 UI 样式使用 QSS (Qt Style Sheets) 定义，可以在对应方法中修改：

**修改按钮颜色**：

```python
# 在 get_button_style 方法中
base_style = """
    QPushButton {
        background-color: rgba(70, 130, 180, 180);  # 修改这里
        color: white;
        border: none;
        border-radius: 5px;
        font-size: 12px;
        font-weight: bold;
    }
"""
```

**修改窗口大小**：

```python
# 在 setup_window_properties 方法中
self.setFixedSize(280, 400)  # 修改为你想要的大小
```

## 故障排除

### 寻路功能不工作

**可能原因**：
1. 游戏不在 1920x1080 分辨率
2. 游戏窗口不是全屏
3. 地图文件不存在
4. 无法识别玩家位置

**解决方法**：
1. 确认游戏分辨率和窗口模式
2. 检查 `maps/` 目录下是否有对应地图文件
3. 检查游戏状态是否为 "in_game"

### 地图识别不准确

**可能原因**：
1. 游戏地图区域被遮挡
2. 地图分类模型未正确加载
3. 截图区域不正确

**解决方法**：
1. 确保 florr.io 标签页在浏览器顶部
2. 检查 `map_classifier/best_model.pth` 文件是否存在
3. 调整截图区域：`(1600, 20, 300, 300)`

### UI 窗口无法显示

**可能原因**：
1. PyQt5 未正确安装
2. 有其他全屏窗口遮挡
3. macOS 权限未授予

**解决方法**：
1. 运行 `pip install PyQt5`
2. 使用 `Cmd+Tab` 切换窗口
3. 在系统偏好设置中授予辅助功能权限

## 性能优化建议

### 减少游戏干扰

1. **降低透明度**：将 UI 透明度设置为 70%-80%
2. **最小化窗口**：不需要时点击最小化按钮
3. **锁定位置**：避免意外移动干扰游戏

### 提高响应速度

1. **优化寻路参数**：根据地图复杂度调整目标位置
2. **减少状态更新频率**：避免频繁更新 UI
3. **使用异步操作**：将耗时操作放在后台线程

## 扩展开发

### 添加新功能按钮

1. 在 `create_quick_actions` 方法的 `buttons` 列表中添加新按钮
2. 在 `on_action_clicked` 方法中添加对应的处理逻辑
3. 如需状态跟踪，在 `__init__` 中添加对应的状态变量

### 集成其他游戏模块

1. 将模块路径添加到 `sys.path`
2. 使用 try-except 处理导入错误
3. 根据模块可用性启用/禁用对应按钮

**示例**：

```python
try:
    from your_module import your_function
    YOUR_FUNCTION_AVAILABLE = True
except ImportError as e:
    print(f"警告: 无法导入模块 - {e}")
    YOUR_FUNCTION_AVAILABLE = False
```

## 总结

游戏悬浮 UI 已成功集成以下功能：

✅ **寻路功能**：完整的自动寻路到目标位置
✅ **地图识别**：使用 CNN 模型自动识别当前地图
✅ **阴阳切换**：快捷切换阴阳花瓣模式
✅ **停止功能**：一键停止所有操作
✅ **状态显示**：实时显示操作状态和结果
✅ **按钮状态**：可视化显示功能激活状态

待实现功能：

⚠️ **自动攻击**：需要实现攻击线程
⚠️ **自动防御**：需要实现防御线程

UI 系统现在可以与 florr-auto-pathing 项目无缝集成，提供便捷的游戏辅助功能。