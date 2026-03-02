"""
Data Collection Window - 数据收集界面
简洁美观的数据收集工具UI
"""

import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QProgressBar, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient


class CircularProgress(QWidget):
    def __init__(self, size: int = 80, parent=None):
        super().__init__(parent)
        self._size = size
        self._value = 0
        self._max_value = 100
        self._color = QColor(52, 199, 89)
        self.setFixedSize(size, size)
    
    def set_value(self, value: int):
        self._value = min(value, self._max_value)
        self.update()
    
    def set_color(self, color: QColor):
        self._color = color
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = self._size // 2
        radius = self._size // 2 - 8
        pen_width = 6
        
        pen = QPen(QColor(60, 60, 70), pen_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(4, 4, self._size - 8, self._size - 8, 0, 360 * 16)
        
        if self._value > 0:
            pen = QPen(self._color, pen_width)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            angle = int(360 * self._value / self._max_value * 16)
            painter.drawArc(4, 4, self._size - 8, self._size - 8, 90 * 16, -angle)
        
        painter.setPen(QColor(255, 255, 255))
        font = QFont('SF Pro Display', 12, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, f'{self._value}')


class StatCard(QFrame):
    def __init__(self, title: str, value: str = "0", parent=None):
        super().__init__(parent)
        self._title = title
        self._value = value
        self._setup_ui()
    
    def _setup_ui(self):
        self.setFixedSize(100, 60)
        self.setStyleSheet("""
            StatCard {
                background: rgba(45, 45, 55, 180);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        
        self._title_label = QLabel(self._title)
        self._title_label.setStyleSheet("color: rgba(255, 255, 255, 150); font-size: 10px;")
        self._title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._title_label)
        
        self._value_label = QLabel(self._value)
        self._value_label.setStyleSheet("color: #34C759; font-size: 16px; font-weight: bold;")
        self._value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._value_label)
    
    def set_value(self, value: str):
        self._value = value
        self._value_label.setText(str(value))


class MapSelector(QFrame):
    map_changed = pyqtSignal(str)
    
    MAPS = [
        ('garden', 'Garden 花园'),
        ('ocean', 'Ocean 海洋'),
        ('desert', 'Desert 沙漠'),
        ('jungle', 'Jungle 丛林'),
        ('hel', 'Hel 地狱'),
        ('factory', 'Factory 工厂'),
        ('anthell', 'Ant Hell 蚂蚁地狱'),
        ('sewers', 'Sewers 下水道'),
        ('pyramid', 'Pyramid 金字塔'),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_map = 'garden'
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            MapSelector {
                background: transparent;
            }
            QComboBox {
                background: rgba(45, 45, 55, 200);
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
                font-size: 13px;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 1px solid rgba(52, 199, 89, 150);
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid rgba(255, 255, 255, 180);
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background: rgba(40, 40, 50, 240);
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 8px;
                selection-background-color: rgba(52, 199, 89, 100);
                color: white;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel('当前地图:')
        label.setStyleSheet("color: rgba(255, 255, 255, 180); font-size: 12px;")
        layout.addWidget(label)
        
        self._combo = QComboBox()
        for map_id, map_name in self.MAPS:
            self._combo.addItem(map_name, map_id)
        self._combo.currentIndexChanged.connect(self._on_map_changed)
        layout.addWidget(self._combo)
    
    def _on_map_changed(self, index):
        self._current_map = self._combo.currentData()
        self.map_changed.emit(self._current_map)
    
    def get_current_map(self) -> str:
        return self._current_map


class ControlButton(QPushButton):
    def __init__(self, text: str, color: str = '#34C759', parent=None):
        super().__init__(text, parent)
        self._color = color
        self._setup_style()
    
    def _setup_style(self):
        self.setFixedSize(120, 44)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: {self._color};
                border: none;
                border-radius: 22px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {self._lighten_color(self._color)};
            }}
            QPushButton:pressed {{
                background: {self._darken_color(self._color)};
            }}
        """)
    
    def _lighten_color(self, color: str) -> str:
        c = QColor(color)
        h, s, l, a = c.getHsl()
        return QColor.fromHsl(h, s, min(l + 20, 255), a).name()
    
    def _darken_color(self, color: str) -> str:
        c = QColor(color)
        h, s, l, a = c.getHsl()
        return QColor.fromHsl(h, s, max(l - 20, 0), a).name()
    
    def set_color(self, color: str):
        self._color = color
        self._setup_style()


class DataCollectionWindow(QWidget):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    map_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._collecting = False
        self._sample_count = 0
        self._session_time = 0
        self._setup_ui()
        self._setup_timer()
    
    def _setup_ui(self):
        self.setFixedSize(380, 280)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._main_widget = QWidget(self)
        self._main_widget.setGeometry(10, 10, 360, 260)
        self._main_widget.setStyleSheet("""
            QWidget {
                background: rgba(30, 30, 35, 230);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
        """)
        
        layout = QVBoxLayout(self._main_widget)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        header_layout = QHBoxLayout()
        
        title = QLabel('📊 数据收集')
        title.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self._status_indicator = QLabel('●')
        self._status_indicator.setStyleSheet("color: #FF3B30; font-size: 12px;")
        header_layout.addWidget(self._status_indicator)
        
        self._status_text = QLabel('待机')
        self._status_text.setStyleSheet("color: rgba(255, 255, 255, 150); font-size: 12px;")
        header_layout.addWidget(self._status_text)
        
        layout.addLayout(header_layout)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: rgba(255, 255, 255, 30); max-height: 1px;")
        layout.addWidget(line)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        
        self._progress = CircularProgress(70)
        stats_layout.addWidget(self._progress)
        
        stats_right = QVBoxLayout()
        stats_right.setSpacing(8)
        
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(8)
        
        self._samples_card = StatCard('样本数', '0')
        cards_layout.addWidget(self._samples_card)
        
        self._time_card = StatCard('时长', '0:00')
        cards_layout.addWidget(self._time_card)
        
        self._rate_card = StatCard('速率', '0/s')
        cards_layout.addWidget(self._rate_card)
        
        stats_right.addLayout(cards_layout)
        
        self._map_selector = MapSelector()
        self._map_selector.map_changed.connect(self._on_map_changed)
        stats_right.addWidget(self._map_selector)
        
        stats_layout.addLayout(stats_right)
        layout.addLayout(stats_layout)
        
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)
        
        self._start_btn = ControlButton('▶ 开始', '#34C759')
        self._start_btn.clicked.connect(self._toggle_collecting)
        controls_layout.addWidget(self._start_btn)
        
        self._save_btn = ControlButton('💾 保存', '#007AFF')
        self._save_btn.clicked.connect(self._on_save)
        controls_layout.addWidget(self._save_btn)
        
        layout.addLayout(controls_layout)
        
        hint = QLabel('提示: 开始后在游戏中正常游玩，系统会自动记录操作')
        hint.setStyleSheet("color: rgba(255, 255, 255, 100); font-size: 10px;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)
    
    def _setup_timer(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_time)
        self._timer.start(1000)
    
    def _update_time(self):
        if self._collecting:
            self._session_time += 1
            mins = self._session_time // 60
            secs = self._session_time % 60
            self._time_card.set_value(f'{mins}:{secs:02d}')
            
            if self._session_time > 0:
                rate = self._sample_count / self._session_time
                self._rate_card.set_value(f'{rate:.1f}/s')
    
    def _toggle_collecting(self):
        if self._collecting:
            self._stop_collecting()
        else:
            self._start_collecting()
    
    def _start_collecting(self):
        self._collecting = True
        self._session_time = 0
        self._sample_count = 0
        
        self._start_btn.setText('⏹ 停止')
        self._start_btn.set_color('#FF3B30')
        self._status_indicator.setStyleSheet("color: #34C759; font-size: 12px;")
        self._status_text.setText('收集中')
        
        self.start_requested.emit()
    
    def _stop_collecting(self):
        self._collecting = False
        
        self._start_btn.setText('▶ 开始')
        self._start_btn.set_color('#34C759')
        self._status_indicator.setStyleSheet("color: #FF9500; font-size: 12px;")
        self._status_text.setText('已暂停')
        
        self.stop_requested.emit()
    
    def _on_map_changed(self, map_name: str):
        self.map_changed.emit(map_name)
    
    def _on_save(self):
        pass
    
    def update_sample_count(self, count: int):
        self._sample_count = count
        self._samples_card.set_value(str(count))
        self._progress.set_value(min(count % 100, 100))
    
    def set_collecting_state(self, collecting: bool):
        if collecting and not self._collecting:
            self._start_collecting()
        elif not collecting and self._collecting:
            self._stop_collecting()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPos() - self._drag_pos)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    window = DataCollectionWindow()
    window.show()
    
    import random
    count = 0
    def update():
        global count
        count += random.randint(1, 5)
        window.update_sample_count(count)
    
    timer = QTimer()
    timer.timeout.connect(update)
    timer.start(100)
    
    sys.exit(app.exec_())
