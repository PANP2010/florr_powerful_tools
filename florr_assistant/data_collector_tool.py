"""
Florr Data Collector - 独立数据收集工具
简单易用的训练数据收集界面
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import signal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from florr_assistant.ui.data_collection_window import DataCollectionWindow
from florr_assistant.core.logger import Logger
from florr_assistant.core.config import Config


class DataCollectionApp:
    def __init__(self):
        self._logger = Logger()
        self._config = Config()
        
        self._collector = None
        self._sample_count = 0
        
        self._setup_app()
        self._setup_collector()
    
    def _setup_app(self):
        self._app = QApplication.instance()
        if self._app is None:
            self._app = QApplication(sys.argv)
        
        self._app.setApplicationName('Florr Data Collector')
        self._app.setStyle('Fusion')
        
        self._window = DataCollectionWindow()
        self._window.start_requested.connect(self._start_collecting)
        self._window.stop_requested.connect(self._stop_collecting)
        self._window.map_changed.connect(self._on_map_changed)
        
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_stats)
        self._update_timer.start(500)
    
    def _setup_collector(self):
        try:
            from florr_assistant.modules.data_collector import DataCollector
            
            self._collector = DataCollector({
                'output_dir': 'data/training',
                'sample_interval': 0.1,
                'auto_save': True,
                'save_interval': 30
            })
            self._collector.start()
            self._collector.add_callback(self._on_sample_collected)
            
            self._logger.info('数据收集器初始化成功', 'DataCollector')
        except Exception as e:
            self._logger.error(f'数据收集器初始化失败: {e}', 'DataCollector')
    
    def _start_collecting(self):
        if self._collector:
            self._collector.start_collecting()
            self._sample_count = 0
            self._logger.info('开始收集数据', 'DataCollector')
    
    def _stop_collecting(self):
        if self._collector:
            self._collector.stop_collecting()
            self._logger.info(f'停止收集，共 {self._sample_count} 条数据', 'DataCollector')
    
    def _on_map_changed(self, map_name: str):
        if self._collector:
            self._collector.set_map(map_name)
            self._logger.info(f'切换地图: {map_name}', 'DataCollector')
    
    def _on_sample_collected(self, sample):
        self._sample_count += 1
    
    def _update_stats(self):
        if self._collector and self._window:
            stats = self._collector.get_stats()
            self._window.update_sample_count(stats['session_samples'])
    
    def run(self):
        self._window.show()
        
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        return self._app.exec_()
    
    def _handle_signal(self, signum, frame):
        self._logger.info('收到退出信号', 'DataCollector')
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self):
        if self._collector:
            self._collector.stop()
        self._logger.info('数据收集器已关闭', 'DataCollector')


def main():
    print("""
╔═══════════════════════════════════════════════════╗
║       Florr Data Collector - 数据收集工具          ║
║                                                   ║
║  使用方法:                                         ║
║  1. 选择当前游戏地图                               ║
║  2. 点击"开始"按钮                                 ║
║  3. 在游戏中正常游玩                               ║
║  4. 系统会自动记录你的操作                         ║
║  5. 点击"停止"结束收集                             ║
║                                                   ║
║  数据保存位置: data/training/                      ║
╚═══════════════════════════════════════════════════╝
    """)
    
    app = DataCollectionApp()
    sys.exit(app.run())


if __name__ == '__main__':
    main()
