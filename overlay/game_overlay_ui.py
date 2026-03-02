import sys
import json
import os
import sys
sys.path.insert(0, '/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/florr-auto-pathing')
sys.path.insert(0, '/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/florr-auto-pathing/map_dataset')

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSlider, 
                             QFrame, QGridLayout, QCheckBox, QGroupBox,
                             QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QPoint, QSize, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QPainter, QBrush, QPen

try:
    from utils import apply_map, get_player_position, check_stage
    from main import lazy_theta_pathing
    from infer_map_classifier_pytorch import predict_from_screenshot
    PATHING_AVAILABLE = True
    MAP_DETECT_AVAILABLE = True
except ImportError as e:
    print(f"警告: 无法导入寻路模块 - {e}")
    PATHING_AVAILABLE = False
    MAP_DETECT_AVAILABLE = False

class FloatingOverlayUI(QMainWindow):
    status_update = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self.config_file = 'ui_config.json'
        self.load_config()
        
        self.pathing_active = False
        self.map_detect_active = False
        self.auto_attack_active = False
        self.auto_defend_active = False
        
        self.init_ui()
        self.setup_window_properties()
        
        self.drag_position = None
        
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        self.create_header()
        self.create_status_display()
        self.create_quick_actions()
        self.create_settings_panel()
        
    def setup_window_properties(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | 
                           Qt.FramelessWindowHint | 
                           Qt.Tool)
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        self.setFixedSize(280, 400)
        
        if self.config.get('position'):
            self.move(*self.config['position'])
        else:
            self.move(100, 100)
        
        self.set_opacity(self.config.get('opacity', 0.85))
        
    def create_header(self):
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 200);
                border-radius: 8px;
                padding: 5px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("游戏助手")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
            }
        """)
        
        min_btn = QPushButton("−")
        min_btn.setFixedSize(30, 25)
        min_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 60, 150);
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
            }
        """)
        min_btn.clicked.connect(self.toggle_minimize)
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 25)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(200, 60, 60, 150);
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(220, 80, 80, 200);
            }
        """)
        close_btn.clicked.connect(self.close)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(min_btn)
        header_layout.addWidget(close_btn)
        
        self.main_layout.addWidget(header)
        
        header.mousePressEvent = self.header_mouse_press
        header.mouseMoveEvent = self.header_mouse_move
        
    def create_status_display(self):
        status_group = QGroupBox("状态")
        status_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 100);
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                color: rgba(200, 220, 255, 255);
                font-size: 11px;
                padding: 5px;
                background-color: rgba(0, 0, 0, 100);
                border-radius: 4px;
            }
        """)
        self.status_label.setWordWrap(True)
        
        status_layout.addWidget(self.status_label)
        self.main_layout.addWidget(status_group)
        
    def get_button_style(self, action_id, is_active):
        base_style = """
            QPushButton {
                background-color: rgba(70, 130, 180, 180);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(100, 150, 200, 220);
            }
            QPushButton:pressed {
                background-color: rgba(50, 100, 150, 200);
            }
        """
        
        active_style = """
            QPushButton {
                background-color: rgba(180, 70, 70, 220);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
                border: 2px solid rgba(255, 200, 200, 255);
            }
            QPushButton:hover {
                background-color: rgba(200, 90, 90, 240);
            }
        """
        
        return active_style if is_active else base_style
    
    def create_quick_actions(self):
        actions_group = QGroupBox("快捷操作")
        actions_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 100);
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        grid_layout = QGridLayout(actions_group)
        grid_layout.setSpacing(8)
        
        buttons = [
            ("寻路", "pathing"),
            ("地图识别", "map_detect"),
            ("自动攻击", "auto_attack"),
            ("自动防御", "auto_defend"),
            ("阴阳切换", "yinyang"),
            ("停止", "stop")
        ]
        
        for i, (text, action_id) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setMinimumHeight(35)
            btn.setProperty("action_id", action_id)
            btn.setStyleSheet(self.get_button_style(action_id, False))
            btn.clicked.connect(lambda checked, aid=action_id: self.on_action_clicked(aid))
            grid_layout.addWidget(btn, i // 2, i % 2)
        
        self.main_layout.addWidget(actions_group)
        
    def create_settings_panel(self):
        settings_group = QGroupBox("设置")
        settings_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 100);
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        settings_layout = QVBoxLayout(settings_group)
        
        opacity_label = QLabel(f"透明度: {int(self.config.get('opacity', 0.85) * 100)}%")
        opacity_label.setStyleSheet("color: white; font-size: 12px;")
        
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setRange(30, 100)
        opacity_slider.setValue(int(self.config.get('opacity', 0.85) * 100))
        opacity_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: rgba(255, 255, 255, 100);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                background: rgba(100, 150, 200, 220);
                border-radius: 8px;
                margin: -5px 0;
            }
        """)
        opacity_slider.valueChanged.connect(self.on_opacity_changed)
        
        settings_layout.addWidget(opacity_label)
        settings_layout.addWidget(opacity_slider)
        
        lock_pos_cb = QCheckBox("锁定位置")
        lock_pos_cb.setChecked(self.config.get('lock_position', False))
        lock_pos_cb.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 12px;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        lock_pos_cb.stateChanged.connect(self.on_lock_position_changed)
        
        settings_layout.addWidget(lock_pos_cb)
        
        self.main_layout.addWidget(settings_group)
        
    def set_opacity(self, value):
        self.setWindowOpacity(value)
        
    def on_opacity_changed(self, value):
        opacity = value / 100.0
        self.set_opacity(opacity)
        self.config['opacity'] = opacity
        self.save_config()
        
        opacity_label = self.findChild(QLabel, "").text()
        for child in self.central_widget.findChildren(QLabel):
            if "透明度" in child.text():
                child.setText(f"透明度: {value}%")
                break
        
    def on_lock_position_changed(self, state):
        self.config['lock_position'] = state == Qt.Checked
        self.save_config()
        
    def toggle_minimize(self):
        if self.isMinimized():
            self.showNormal()
        else:
            self.showMinimized()
            
    def on_action_clicked(self, action_id):
        print(f"Action clicked: {action_id}")
        
        if action_id == "pathing":
            if not PATHING_AVAILABLE:
                QMessageBox.warning(self, "功能不可用", "寻路模块未找到")
                return
            
            if self.pathing_active:
                self.pathing_active = False
                self.update_status("寻路已停止")
            else:
                try:
                    self.pathing_active = True
                    self.update_status("正在寻路...")
                    
                    stage = check_stage()
                    if stage != "in_game":
                        self.pathing_active = False
                        self.update_status(f"游戏状态: {stage}")
                        return
                    
                    pos = get_player_position()
                    if pos is None:
                        self.pathing_active = False
                        self.update_status("无法获取玩家位置")
                        return
                    
                    class_name, conf = predict_from_screenshot()
                    self.update_status(f"当前地图: {class_name} (置信度: {conf:.1%})")
                    
                    apply_map(class_name)
                    
                    location = (100, 100)
                    dedicated_area = []
                    
                    result = lazy_theta_pathing(location, dedicated_area)
                    self.pathing_active = False
                    
                    if result:
                        self.update_status("寻路完成！")
                    else:
                        self.update_status("寻路失败")
                        
                except Exception as e:
                    self.pathing_active = False
                    self.update_status(f"寻路错误: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
        elif action_id == "map_detect":
            if not MAP_DETECT_AVAILABLE:
                QMessageBox.warning(self, "功能不可用", "地图识别模块未找到")
                return
            
            try:
                self.map_detect_active = True
                self.update_status("正在识别地图...")
                
                class_name, conf = predict_from_screenshot()
                self.map_detect_active = False
                
                self.update_status(f"识别结果: {class_name} (置信度: {conf:.1%})")
                
            except Exception as e:
                self.map_detect_active = False
                self.update_status(f"识别错误: {str(e)}")
                import traceback
                traceback.print_exc()
                
        elif action_id == "auto_attack":
            self.auto_attack_active = not self.auto_attack_active
            status = "自动攻击: 开启" if self.auto_attack_active else "自动攻击: 关闭"
            self.update_status(status)
            self.update_button_styles()
            
        elif action_id == "auto_defend":
            self.auto_defend_active = not self.auto_defend_active
            status = "自动防御: 开启" if self.auto_defend_active else "自动防御: 关闭"
            self.update_status(status)
            self.update_button_styles()
            
        elif action_id == "yinyang":
            try:
                import pyautogui
                pyautogui.press('2')
                self.update_status("已切换阴阳模式")
            except:
                self.update_status("切换失败")
                
        elif action_id == "stop":
            self.pathing_active = False
            self.map_detect_active = False
            self.auto_attack_active = False
            self.auto_defend_active = False
            self.update_status("所有操作已停止")
            
    def update_status(self, message):
        print(f"[状态] {message}")
        
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
        
    def header_mouse_press(self, event):
        if not self.config.get('lock_position', False):
            if event.button() == Qt.LeftButton:
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                
    def header_mouse_move(self, event):
        if self.drag_position and not self.config.get('lock_position', False):
            self.move(event.globalPos() - self.drag_position)
            
    def mousePressEvent(self, event):
        if not self.config.get('lock_position', False):
            if event.button() == Qt.LeftButton:
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                
    def mouseMoveEvent(self, event):
        if self.drag_position and not self.config.get('lock_position', False):
            self.move(event.globalPos() - self.drag_position)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = None
            self.config['position'] = [self.x(), self.y()]
            self.save_config()
            
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except:
                self.config = {}
        else:
            self.config = {}
            
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        bg_color = QColor(30, 30, 30, int(self.config.get('opacity', 0.85) * 255))
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(100, 100, 100, 150), 2))
        
        painter.drawRoundedRect(self.rect(), 10, 10)
        
    def closeEvent(self, event):
        self.config['position'] = [self.x(), self.y()]
        self.save_config()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = FloatingOverlayUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()