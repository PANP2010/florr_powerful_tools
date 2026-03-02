"""
Main Window - 主窗口
现代化UI设计，支持亮色/暗色主题
"""

import sys
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QGridLayout,
    QSizePolicy, QStatusBar, QSystemTrayIcon, QMenu, QAction,
    QTabWidget, QPlainTextEdit, QProgressBar, QCheckBox,
    QComboBox, QSlider, QSpinBox, QGroupBox, QLineEdit,
    QMessageBox, QFileDialog,
)
from PyQt5.QtCore import (
    Qt, QTimer, QSize, pyqtSignal, QThread, QPropertyAnimation,
    QEasingCurve, QPoint,
)
from PyQt5.QtGui import (
    QIcon, QFont, QColor, QPalette, QPixmap, QPainter, QPen,
    QLinearGradient, QFontDatabase,
)

from .styles import Styles, Theme


class StatusCard(QFrame):
    clicked = pyqtSignal(str)
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._title = title
        self._status = 'stopped'
        self._value = '0'
        
        self.setObjectName('statusCard')
        self.setFixedSize(180, 100)
        self.setCursor(Qt.PointingHandCursor)
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(6)
        
        self._title_label = QLabel(self._title)
        self._title_label.setObjectName('cardTitle')
        layout.addWidget(self._title_label)
        
        self._value_label = QLabel(self._value)
        self._value_label.setObjectName('cardValue')
        layout.addWidget(self._value_label)
        
        self._status_label = QLabel('已停止')
        self._status_label.setObjectName('cardStatus')
        layout.addWidget(self._status_label)
        
        layout.addStretch()
    
    def set_value(self, value: str):
        self._value = value
        self._value_label.setText(value)
    
    def set_status(self, status: str, text: str = None):
        self._status = status
        status_texts = {
            'running': '运行中',
            'paused': '已暂停',
            'stopped': '已停止',
            'error': '错误',
        }
        self._status_label.setText(text or status_texts.get(status, status))
        
        self._status_label.setStyleSheet('')
        if status == 'running':
            self._status_label.setStyleSheet('color: #4CAF50;')
        elif status == 'paused':
            self._status_label.setStyleSheet('color: #FF9800;')
        elif status == 'error':
            self._status_label.setStyleSheet('color: #F44336;')
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._title)


class LogWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('logText')
        self.setReadOnly(True)
        self.setMaximumBlockCount(500)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        
        font = QFont('SF Mono', 11)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
    
    def append_log(self, level: str, module: str, message: str):
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        colors = {
            'DEBUG': '#888888',
            'INFO': '#4CAF50',
            'WARNING': '#FF9800',
            'ERROR': '#F44336',
            'CRITICAL': '#E91E63',
        }
        color = colors.get(level.upper(), '#FFFFFF')
        
        html = f'<span style="color: #888;">[{timestamp}]</span> '
        html += f'<span style="color: {color};">[{level}]</span> '
        html += f'<span style="color: #64B5F6;">[{module}]</span> '
        html += f'<span>{message}</span>'
        
        self.appendHtml(html)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


class MainWindow(QMainWindow):
    def __init__(self, app=None):
        super().__init__()
        self._app = app
        self._styles = Styles(Theme.DARK)
        
        self._start_time = None
        self._stats = {
            'petals': 0,
            'kills': 0,
            'deaths': 0,
        }
        
        self._setup_window()
        self._setup_ui()
        self._setup_tray()
        self._setup_timers()
        
        self._connect_signals()
        
        self._add_log('INFO', 'Main', 'Florr Assistant 已启动')
        self._add_log('INFO', 'Main', f'平台: {self._app.platform.type.value if self._app else "unknown"}')
    
    def _setup_window(self):
        self.setWindowTitle('Florr Assistant')
        self.setMinimumSize(900, 650)
        self.resize(1000, 700)
        
        self.setStyleSheet(self._styles.get_stylesheet())
        
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowSystemMenuHint |
            Qt.WindowMinMaxButtonsHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)
    
    def _setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName('centralWidget')
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        main_layout.addWidget(self._create_title_bar())
        main_layout.addWidget(self._create_content(), stretch=1)
        main_layout.addWidget(self._create_bottom_bar())
    
    def _create_title_bar(self) -> QWidget:
        title_bar = QWidget()
        title_bar.setObjectName('titleBar')
        title_bar.setFixedHeight(48)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(16, 0, 8, 0)
        
        icon_label = QLabel('🌸')
        icon_label.setStyleSheet('font-size: 20px;')
        layout.addWidget(icon_label)
        
        title_label = QLabel('Florr Assistant')
        title_label.setObjectName('titleLabel')
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        self._theme_btn = QPushButton('🌙')
        self._theme_btn.setFixedSize(36, 36)
        self._theme_btn.setObjectName('secondaryButton')
        self._theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self._theme_btn)
        
        min_btn = QPushButton('─')
        min_btn.setFixedSize(36, 36)
        min_btn.setObjectName('secondaryButton')
        min_btn.clicked.connect(self.showMinimized)
        layout.addWidget(min_btn)
        
        max_btn = QPushButton('□')
        max_btn.setFixedSize(36, 36)
        max_btn.setObjectName('secondaryButton')
        max_btn.clicked.connect(self._toggle_maximize)
        layout.addWidget(max_btn)
        
        close_btn = QPushButton('×')
        close_btn.setFixedSize(36, 36)
        close_btn.setObjectName('dangerButton')
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self._drag_pos = None
        return title_bar
    
    def _create_content(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        layout.addWidget(self._create_status_cards())
        layout.addWidget(self._create_main_area(), stretch=1)
        
        return content
    
    def _create_status_cards(self) -> QWidget:
        cards_widget = QWidget()
        layout = QHBoxLayout(cards_widget)
        layout.setSpacing(15)
        
        self._afk_card = StatusCard('AFK防护')
        self._afk_card.clicked.connect(self._on_card_clicked)
        layout.addWidget(self._afk_card)
        
        self._pathing_card = StatusCard('自动寻路')
        self._pathing_card.clicked.connect(self._on_card_clicked)
        layout.addWidget(self._pathing_card)
        
        self._combat_card = StatusCard('自动战斗')
        self._combat_card.clicked.connect(self._on_card_clicked)
        layout.addWidget(self._combat_card)
        
        self._stats_card = StatusCard('数据统计')
        self._stats_card.clicked.connect(self._on_card_clicked)
        layout.addWidget(self._stats_card)
        
        layout.addStretch()
        return cards_widget
    
    def _create_main_area(self) -> QWidget:
        main_area = QWidget()
        layout = QHBoxLayout(main_area)
        layout.setSpacing(15)
        
        left_panel = self._create_info_panel()
        layout.addWidget(left_panel, stretch=1)
        
        right_panel = self._create_log_panel()
        layout.addWidget(right_panel, stretch=1)
        
        return main_area
    
    def _create_info_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName('statusCard')
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        title = QLabel('实时信息')
        title.setStyleSheet('font-size: 14px; font-weight: bold;')
        layout.addWidget(title)
        
        self._info_labels = {}
        info_items = [
            ('map', '当前地图', '-'),
            ('time', '运行时间', '00:00:00'),
            ('petals', '收集花瓣', '0'),
            ('kills', '击杀数', '0'),
            ('efficiency', '效率', '-/h'),
        ]
        
        for key, label, default in info_items:
            row = QHBoxLayout()
            name_label = QLabel(label)
            name_label.setStyleSheet('color: #888;')
            value_label = QLabel(default)
            value_label.setStyleSheet('font-weight: bold;')
            value_label.setAlignment(Qt.AlignRight)
            row.addWidget(name_label)
            row.addStretch()
            row.addWidget(value_label)
            layout.addLayout(row)
            self._info_labels[key] = value_label
        
        layout.addStretch()
        return panel
    
    def _create_log_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName('statusCard')
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        title = QLabel('日志输出')
        title.setStyleSheet('font-size: 14px; font-weight: bold;')
        layout.addWidget(title)
        
        self._log_widget = LogWidget()
        layout.addWidget(self._log_widget)
        
        return panel
    
    def _create_bottom_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName('titleBar')
        bar.setFixedHeight(60)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)
        
        self._start_btn = QPushButton('▶ 开始全部')
        self._start_btn.setMinimumWidth(120)
        self._start_btn.clicked.connect(self._start_all)
        layout.addWidget(self._start_btn)
        
        self._stop_btn = QPushButton('■ 停止全部')
        self._stop_btn.setMinimumWidth(120)
        self._stop_btn.setObjectName('dangerButton')
        self._stop_btn.clicked.connect(self._stop_all)
        self._stop_btn.setEnabled(False)
        layout.addWidget(self._stop_btn)
        
        layout.addStretch()
        
        settings_btn = QPushButton('⚙ 设置')
        settings_btn.setObjectName('secondaryButton')
        settings_btn.clicked.connect(self._show_settings)
        layout.addWidget(settings_btn)
        
        about_btn = QPushButton('ℹ 关于')
        about_btn.setObjectName('secondaryButton')
        about_btn.clicked.connect(self._show_about)
        layout.addWidget(about_btn)
        
        return bar
    
    def _setup_tray(self):
        self._tray_icon = QSystemTrayIcon(self)
        self._tray_icon.setIcon(QIcon.fromTheme('application-x-executable'))
        
        tray_menu = QMenu()
        
        show_action = QAction('显示窗口', self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        start_action = QAction('开始', self)
        start_action.triggered.connect(self._start_all)
        tray_menu.addAction(start_action)
        
        stop_action = QAction('停止', self)
        stop_action.triggered.connect(self._stop_all)
        tray_menu.addAction(stop_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction('退出', self)
        quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(quit_action)
        
        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.show()
    
    def _setup_timers(self):
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_ui)
        self._update_timer.start(1000)
    
    def _connect_signals(self):
        if self._app:
            self._app.logger.add_callback(self._on_log_record)
    
    def _on_log_record(self, record):
        self._log_widget.append_log(record.level, record.module, record.message)
    
    def _add_log(self, level, module, message):
        self._log_widget.append_log(level, module, message)
        if self._app:
            self._app.logger._add_to_history(level, module, message)
    
    def _toggle_theme(self):
        self._styles.toggle_theme()
        self.setStyleSheet(self._styles.get_stylesheet())
        self._theme_btn.setText('☀️' if self._styles.theme == Theme.LIGHT else '🌙')
    
    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def _on_card_clicked(self, card_name: str):
        self._add_log('DEBUG', 'UI', f'卡片点击: {card_name}')
    
    def _start_all(self):
        self._add_log('INFO', 'Main', '正在启动所有模块...')
        
        self._start_time = time.time()
        
        self._afk_card.set_status('running')
        self._pathing_card.set_status('running')
        self._combat_card.set_status('running')
        self._stats_card.set_status('running')
        
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        
        if self._app:
            self._app.start_all()
        
        self._add_log('INFO', 'Main', '所有模块已启动')
    
    def _stop_all(self):
        self._add_log('INFO', 'Main', '正在停止所有模块...')
        
        self._afk_card.set_status('stopped')
        self._pathing_card.set_status('stopped')
        self._combat_card.set_status('stopped')
        self._stats_card.set_status('stopped')
        
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        
        if self._app:
            self._app.stop_all()
        
        self._add_log('INFO', 'Main', '所有模块已停止')
    
    def _update_ui(self):
        if self._start_time:
            elapsed = time.time() - self._start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self._info_labels['time'].setText(f'{hours:02d}:{minutes:02d}:{seconds:02d}')
        
        if self._app and self._app.is_running:
            stats = self._app.engine.get_stats()
            self._info_labels['petals'].setText(str(self._stats['petals']))
            self._info_labels['kills'].setText(str(self._stats['kills']))
    
    def _show_settings(self):
        QMessageBox.information(self, '设置', '设置功能开发中...')
    
    def _show_about(self):
        QMessageBox.about(
            self,
            '关于 Florr Assistant',
            '<h2>Florr Assistant</h2>'
            '<p>版本: 1.0.0</p>'
            '<p>智能florr.io游戏辅助工具</p>'
            '<hr>'
            '<p>功能特性:</p>'
            '<ul>'
            '<li>AFK自动防护</li>'
            '<li>智能寻路导航</li>'
            '<li>自动战斗刷怪</li>'
            '<li>数据统计分析</li>'
            '</ul>'
            '<hr>'
            '<p>© 2026 Florr Powerful Tools Team</p>'
        )
    
    def _quit_app(self):
        if self._app:
            self._app.shutdown()
        QApplication.quit()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
    
    def mouseReleaseEvent(self, event):
        self._drag_pos = None
    
    def closeEvent(self, event):
        if self._app and self._app.config.get('general.minimize_to_tray', True):
            event.ignore()
            self.hide()
            self._tray_icon.showMessage(
                'Florr Assistant',
                '程序已最小化到系统托盘',
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self._quit_app()
    
    def run(self):
        self.show()
        sys.exit(QApplication.instance().exec_() if QApplication.instance() else QApplication(sys.argv).exec_())
