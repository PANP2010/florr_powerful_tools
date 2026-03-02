"""
Modern Overlay Window - 现代透明悬浮窗
透明、圆形设计语言、极简风格
"""

import sys
import time
from typing import Optional, Dict, Any
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect,
    QSizePolicy, QSpacerItem,
)
from PyQt5.QtCore import (
    Qt, QTimer, QSize, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QPoint, QRectF, pyqtProperty,
)
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPainterPath,
    QLinearGradient, QRadialGradient, QFontDatabase,
)


class CircularProgress(QWidget):
    def __init__(self, size: int = 50, parent=None):
        super().__init__(parent)
        self._size = size
        self._progress = 0.0
        self._color = QColor(100, 181, 246)
        self._bg_color = QColor(255, 255, 255, 30)
        
        self.setFixedSize(size, size)
    
    def setProgress(self, value: float):
        self._progress = max(0, min(1, value))
        self.update()
    
    def setColor(self, color: QColor):
        self._color = color
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = self._size // 2
        radius = self._size // 2 - 4
        pen_width = 3
        
        pen = QPen(self._bg_color)
        pen.setWidth(pen_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawEllipse(center, center, radius, radius)
        
        if self._progress > 0:
            gradient = QLinearGradient(0, 0, self._size, self._size)
            gradient.setColorAt(0, self._color)
            gradient.setColorAt(1, self._color.lighter(120))
            
            pen = QPen(QBrush(gradient), pen_width)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            
            angle = int(5760 * self._progress)
            painter.drawArc(4, 4, self._size - 8, self._size - 8, 1440, -angle)


class CircleButton(QPushButton):
    def __init__(self, icon_text: str = "", size: int = 44, parent=None):
        super().__init__(parent)
        self._size = size
        self._icon_text = icon_text
        self._bg_color = QColor(255, 255, 255, 40)
        self._hover_color = QColor(255, 255, 255, 60)
        self._active_color = QColor(100, 181, 246, 180)
        self._is_active = False
        self._is_hovering = False
        
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
    
    def setActive(self, active: bool):
        self._is_active = active
        self.update()
    
    def isActive(self) -> bool:
        return self._is_active
    
    def enterEvent(self, event):
        self._is_hovering = True
        self.update()
    
    def leaveEvent(self, event):
        self._is_hovering = False
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = self._size // 2
        radius = self._size // 2 - 2
        
        if self._is_active:
            color = self._active_color
        elif self._is_hovering:
            color = self._hover_color
        else:
            color = self._bg_color
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(center, center, radius, radius)
        
        if self._is_active:
            glow = QRadialGradient(center, center, radius + 5)
            glow.setColorAt(0.7, QColor(100, 181, 246, 50))
            glow.setColorAt(1, QColor(100, 181, 246, 0))
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(center, center, radius + 5, radius + 5)
        
        painter.setPen(QPen(QColor(255, 255, 255, 200)))
        painter.setFont(QFont("SF Pro Display", 14, QFont.Bold))
        painter.drawText(QRectF(0, 0, self._size, self._size), Qt.AlignCenter, self._icon_text)


class StatusIndicator(QWidget):
    def __init__(self, size: int = 8, parent=None):
        super().__init__(parent)
        self._size = size
        self._color = QColor(158, 158, 158)
        self._pulse = False
        
        self.setFixedSize(size, size)
        
        self._pulse_timer = QTimer()
        self._pulse_timer.timeout.connect(self._on_pulse)
        self._pulse_opacity = 1.0
    
    def setStatus(self, status: str):
        colors = {
            'running': QColor(129, 199, 132),
            'paused': QColor(255, 183, 77),
            'stopped': QColor(158, 158, 158),
            'error': QColor(229, 115, 115),
        }
        self._color = colors.get(status, QColor(158, 158, 158))
        
        if status == 'running':
            self._pulse = True
            self._pulse_timer.start(50)
        else:
            self._pulse = False
            self._pulse_timer.stop()
        
        self.update()
    
    def _on_pulse(self):
        import math
        self._pulse_opacity = 0.6 + 0.4 * math.sin(time.time() * 4)
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        color = QColor(self._color)
        color.setAlphaF(self._pulse_opacity if self._pulse else 1.0)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(self._size // 2, self._size // 2, self._size // 2 - 1, self._size // 2 - 1)


class MiniStatCard(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._title = title
        self._value = "0"
        self._status = "stopped"
        
        self.setFixedSize(70, 50)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        
        top_row = QHBoxLayout()
        top_row.setSpacing(4)
        
        self._indicator = StatusIndicator(6)
        top_row.addWidget(self._indicator)
        
        self._title_label = QLabel(self._title)
        self._title_label.setStyleSheet("color: rgba(255,255,255,120); font-size: 10px;")
        top_row.addWidget(self._title_label)
        top_row.addStretch()
        
        layout.addLayout(top_row)
        
        self._value_label = QLabel(self._value)
        self._value_label.setStyleSheet("color: rgba(255,255,255,230); font-size: 16px; font-weight: bold;")
        layout.addWidget(self._value_label)
    
    def setValue(self, value: str):
        self._value = value
        self._value_label.setText(value)
    
    def setStatus(self, status: str):
        self._status = status
        self._indicator.setStatus(status)


class ModernOverlayWindow(QWidget):
    def __init__(self, app=None):
        super().__init__()
        self._app = app
        
        self._start_time = None
        self._stats = {'petals': 0, 'kills': 0}
        self._module_states = {
            'afk': 'stopped',
            'pathing': 'stopped',
            'combat': 'stopped',
            'stats': 'stopped',
        }
        
        self._setup_window()
        self._setup_ui()
        self._setup_timers()
        self._apply_styles()
        
        self._old_pos = None
    
    def _setup_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        self.setFixedSize(320, 180)
        self.move(20, 80)
    
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(8)
        
        container = QFrame()
        container.setObjectName("container")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(12, 10, 12, 10)
        container_layout.setSpacing(8)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        self._progress_ring = CircularProgress(36)
        header_layout.addWidget(self._progress_ring)
        
        title_info = QVBoxLayout()
        title_info.setSpacing(2)
        
        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        
        title_label = QLabel("Florr")
        title_label.setObjectName("title")
        title_row.addWidget(title_label)
        
        self._time_label = QLabel("00:00")
        self._time_label.setObjectName("time")
        title_row.addWidget(self._time_label)
        title_row.addStretch()
        
        title_info.addLayout(title_row)
        
        self._status_label = QLabel("就绪")
        self._status_label.setObjectName("status")
        title_info.addWidget(self._status_label)
        
        header_layout.addLayout(title_info)
        header_layout.addStretch()
        
        container_layout.addLayout(header_layout)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(6)
        
        self._stat_cards = {}
        for name, title in [('afk', 'AFK'), ('combat', '战斗'), ('stats', '统计')]:
            card = MiniStatCard(title)
            self._stat_cards[name] = card
            stats_layout.addWidget(card)
        
        container_layout.addLayout(stats_layout)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        buttons_layout.addStretch()
        
        self._btn_afk = CircleButton("A", 36)
        self._btn_afk.setToolTip("AFK防护")
        self._btn_afk.clicked.connect(lambda: self._toggle_module('afk'))
        buttons_layout.addWidget(self._btn_afk)
        
        self._btn_pathing = CircleButton("P", 36)
        self._btn_pathing.setToolTip("自动寻路")
        self._btn_pathing.clicked.connect(lambda: self._toggle_module('pathing'))
        buttons_layout.addWidget(self._btn_pathing)
        
        self._btn_combat = CircleButton("⚔", 36)
        self._btn_combat.setToolTip("自动战斗")
        self._btn_combat.clicked.connect(lambda: self._toggle_module('combat'))
        buttons_layout.addWidget(self._btn_combat)
        
        self._btn_main = CircleButton("▶", 40)
        self._btn_main.setToolTip("开始/停止全部")
        self._btn_main.clicked.connect(self._toggle_all)
        buttons_layout.addWidget(self._btn_main)
        
        buttons_layout.addStretch()
        
        container_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(container)
    
    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget#container {
                background: rgba(30, 30, 35, 200);
                border-radius: 16px;
            }
            
            QLabel#title {
                color: rgba(255, 255, 255, 230);
                font-size: 14px;
                font-weight: bold;
            }
            
            QLabel#time {
                color: rgba(100, 181, 246, 200);
                font-size: 12px;
                font-family: "SF Mono", monospace;
            }
            
            QLabel#status {
                color: rgba(255, 255, 255, 100);
                font-size: 11px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.findChild(QFrame, "container").setGraphicsEffect(shadow)
    
    def _setup_timers(self):
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_ui)
        self._update_timer.start(1000)
    
    def _toggle_module(self, module_name: str):
        current = self._module_states.get(module_name, 'stopped')
        
        if current == 'running':
            self._module_states[module_name] = 'stopped'
            self._status_label.setText(f"{module_name.upper()} 已停止")
        else:
            self._module_states[module_name] = 'running'
            self._status_label.setText(f"{module_name.upper()} 运行中")
        
        self._update_buttons()
        
        if self._app:
            if self._module_states[module_name] == 'running':
                self._app.start_module(f'{module_name}_detector' if module_name == 'afk' else module_name)
            else:
                self._app.stop_module(f'{module_name}_detector' if module_name == 'afk' else module_name)
    
    def _toggle_all(self):
        all_running = all(s == 'running' for s in self._module_states.values())
        
        if all_running:
            for key in self._module_states:
                self._module_states[key] = 'stopped'
            self._start_time = None
            self._status_label.setText("已停止")
            self._btn_main._icon_text = "▶"
            if self._app:
                self._app.stop_all()
        else:
            for key in self._module_states:
                self._module_states[key] = 'running'
            self._start_time = time.time()
            self._status_label.setText("运行中")
            self._btn_main._icon_text = "■"
            if self._app:
                self._app.start_all()
        
        self._update_buttons()
    
    def _update_buttons(self):
        self._btn_afk.setActive(self._module_states['afk'] == 'running')
        self._btn_pathing.setActive(self._module_states['pathing'] == 'running')
        self._btn_combat.setActive(self._module_states['combat'] == 'running')
        
        self._stat_cards['afk'].setStatus(self._module_states['afk'])
        self._stat_cards['combat'].setStatus(self._module_states['combat'])
        self._stat_cards['stats'].setStatus(self._module_states['stats'])
        
        running_count = sum(1 for s in self._module_states.values() if s == 'running')
        self._progress_ring.setProgress(running_count / 4)
    
    def _update_ui(self):
        if self._start_time:
            elapsed = time.time() - self._start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self._time_label.setText(f"{minutes:02d}:{seconds:02d}")
            
            if self._app and self._app.is_running:
                stats = self._app.engine.get_stats()
                self._stat_cards['stats'].setValue(str(stats.get('modules_run', 0)))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._old_pos = event.globalPos() - self.pos()
    
    def mouseMoveEvent(self, event):
        if self._old_pos is not None:
            self.move(event.globalPos() - self._old_pos)
    
    def mouseReleaseEvent(self, event):
        self._old_pos = None
    
    def contextMenuEvent(self, event):
        from PyQt5.QtWidgets import QMenu, QAction
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: rgba(40, 40, 45, 240);
                color: white;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: rgba(100, 181, 246, 100);
            }
        """)
        
        reset_action = QAction("重置位置", self)
        reset_action.triggered.connect(lambda: self.move(20, 80))
        menu.addAction(reset_action)
        
        menu.addSeparator()
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(quit_action)
        
        menu.exec_(event.globalPos())
    
    def _quit_app(self):
        if self._app:
            self._app.shutdown()
        QApplication.quit()
    
    def run(self):
        self.show()
        app = QApplication.instance()
        if app:
            app.exec_()
