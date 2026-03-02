"""
Styles - 样式定义
支持亮色/暗色主题
"""

from dataclasses import dataclass
from typing import Dict, Tuple
from enum import Enum


class Theme(Enum):
    LIGHT = 'light'
    DARK = 'dark'


@dataclass
class ColorScheme:
    primary: str
    secondary: str
    success: str
    warning: str
    danger: str
    background: str
    surface: str
    surface_hover: str
    text: str
    text_secondary: str
    border: str
    shadow: str


LIGHT_COLORS = ColorScheme(
    primary='#4A90D9',
    secondary='#7B68EE',
    success='#4CAF50',
    warning='#FF9800',
    danger='#F44336',
    background='#FFFFFF',
    surface='#F5F5F5',
    surface_hover='#EEEEEE',
    text='#212121',
    text_secondary='#757575',
    border='#E0E0E0',
    shadow='#00000020',
)

DARK_COLORS = ColorScheme(
    primary='#64B5F6',
    secondary='#9575CD',
    success='#81C784',
    warning='#FFB74D',
    danger='#E57373',
    background='#121212',
    surface='#1E1E1E',
    surface_hover='#2D2D2D',
    text='#FFFFFF',
    text_secondary='#B0B0B0',
    border='#3D3D3D',
    shadow='#00000040',
)


class Styles:
    def __init__(self, theme: Theme = Theme.DARK):
        self._theme = theme
        self._colors = DARK_COLORS if theme == Theme.DARK else LIGHT_COLORS
    
    @property
    def colors(self) -> ColorScheme:
        return self._colors
    
    @property
    def theme(self) -> Theme:
        return self._theme
    
    def set_theme(self, theme: Theme):
        self._theme = theme
        self._colors = DARK_COLORS if theme == Theme.DARK else LIGHT_COLORS
    
    def toggle_theme(self):
        self.set_theme(Theme.LIGHT if self._theme == Theme.DARK else Theme.DARK)
    
    def get_stylesheet(self) -> str:
        c = self._colors
        return f'''
        /* 全局样式 */
        QWidget {{
            font-family: "SF Pro Display", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
            font-size: 13px;
        }}
        
        QMainWindow {{
            background-color: {c.background};
        }}
        
        /* 中央部件 */
        QWidget#centralWidget {{
            background-color: {c.background};
        }}
        
        /* 标题栏 */
        QWidget#titleBar {{
            background-color: {c.surface};
            border-bottom: 1px solid {c.border};
            min-height: 48px;
            max-height: 48px;
        }}
        
        QLabel#titleLabel {{
            color: {c.text};
            font-size: 16px;
            font-weight: bold;
            padding-left: 10px;
        }}
        
        /* 状态卡片 */
        QWidget#statusCard {{
            background-color: {c.surface};
            border: 1px solid {c.border};
            border-radius: 8px;
            padding: 15px;
        }}
        
        QWidget#statusCard:hover {{
            background-color: {c.surface_hover};
            border-color: {c.primary};
        }}
        
        QLabel#cardTitle {{
            color: {c.text_secondary};
            font-size: 12px;
        }}
        
        QLabel#cardValue {{
            color: {c.text};
            font-size: 24px;
            font-weight: bold;
        }}
        
        QLabel#cardStatus {{
            color: {c.success};
            font-size: 11px;
        }}
        
        QLabel#cardStatus.warning {{
            color: {c.warning};
        }}
        
        QLabel#cardStatus.error {{
            color: {c.danger};
        }}
        
        /* 按钮 */
        QPushButton {{
            background-color: {c.primary};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {c.primary}dd;
        }}
        
        QPushButton:pressed {{
            background-color: {c.primary}aa;
        }}
        
        QPushButton:disabled {{
            background-color: {c.surface};
            color: {c.text_secondary};
        }}
        
        QPushButton#secondaryButton {{
            background-color: {c.surface};
            color: {c.text};
            border: 1px solid {c.border};
        }}
        
        QPushButton#secondaryButton:hover {{
            background-color: {c.surface_hover};
            border-color: {c.primary};
        }}
        
        QPushButton#dangerButton {{
            background-color: {c.danger};
        }}
        
        QPushButton#dangerButton:hover {{
            background-color: {c.danger}dd;
        }}
        
        /* 输入框 */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {c.surface};
            color: {c.text};
            border: 1px solid {c.border};
            border-radius: 6px;
            padding: 8px 12px;
            selection-background-color: {c.primary}40;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {c.primary};
        }}
        
        /* 下拉框 */
        QComboBox {{
            background-color: {c.surface};
            color: {c.text};
            border: 1px solid {c.border};
            border-radius: 6px;
            padding: 8px 12px;
            min-width: 120px;
        }}
        
        QComboBox:hover {{
            border-color: {c.primary};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {c.text_secondary};
            margin-right: 10px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {c.surface};
            color: {c.text};
            border: 1px solid {c.border};
            selection-background-color: {c.primary}40;
        }}
        
        /* 复选框 */
        QCheckBox {{
            color: {c.text};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {c.border};
            border-radius: 4px;
            background-color: {c.surface};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {c.primary};
            border-color: {c.primary};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {c.primary};
        }}
        
        /* 滑块 */
        QSlider::groove:horizontal {{
            background: {c.surface};
            height: 6px;
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background: {c.primary};
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {c.primary}dd;
        }}
        
        /* 进度条 */
        QProgressBar {{
            background-color: {c.surface};
            border: none;
            border-radius: 4px;
            height: 8px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {c.primary};
            border-radius: 4px;
        }}
        
        /* 滚动区域 */
        QScrollArea {{
            background-color: transparent;
            border: none;
        }}
        
        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}
        
        QScrollBar:vertical {{
            background-color: {c.surface};
            width: 10px;
            border-radius: 5px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {c.border};
            border-radius: 4px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {c.text_secondary};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        
        /* 分组框 */
        QGroupBox {{
            color: {c.text};
            font-weight: bold;
            border: 1px solid {c.border};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            background-color: {c.background};
        }}
        
        /* 选项卡 */
        QTabWidget::pane {{
            border: 1px solid {c.border};
            border-radius: 8px;
            background-color: {c.background};
        }}
        
        QTabBar::tab {{
            background-color: {c.surface};
            color: {c.text_secondary};
            padding: 10px 20px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {c.background};
            color: {c.text};
            border-bottom: 2px solid {c.primary};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {c.surface_hover};
        }}
        
        /* 日志文本框 */
        QPlainTextEdit#logText {{
            background-color: {c.surface};
            color: {c.text};
            border: 1px solid {c.border};
            border-radius: 6px;
            font-family: "SF Mono", "Consolas", "Monaco", monospace;
            font-size: 12px;
            padding: 8px;
        }}
        
        /* 工具提示 */
        QToolTip {{
            background-color: {c.surface};
            color: {c.text};
            border: 1px solid {c.border};
            border-radius: 4px;
            padding: 6px 10px;
        }}
        
        /* 菜单 */
        QMenu {{
            background-color: {c.surface};
            color: {c.text};
            border: 1px solid {c.border};
            border-radius: 6px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 8px 24px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {c.primary}40;
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {c.border};
            margin: 4px 8px;
        }}
        
        /* 状态栏 */
        QStatusBar {{
            background-color: {c.surface};
            color: {c.text_secondary};
            border-top: 1px solid {c.border};
        }}
        
        /* 分隔线 */
        QFrame[frameShape="4"] {{
            background-color: {c.border};
            max-height: 1px;
        }}
        
        QFrame[frameShape="5"] {{
            background-color: {c.border};
            max-width: 1px;
        }}
        '''
