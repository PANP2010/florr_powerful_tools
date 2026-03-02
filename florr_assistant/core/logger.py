"""
Logger Manager - 日志管理器
支持多级别日志、文件输出、控制台输出
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass
import threading
import queue


@dataclass
class LogRecord:
    timestamp: datetime
    level: str
    module: str
    message: str
    extra: Dict = None


class Logger:
    _instance = None
    _lock = threading.Lock()
    
    LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        name: str = 'FlorrAssistant',
        level: str = 'INFO',
        log_dir: Optional[str] = None,
        console_output: bool = True,
        file_output: bool = True,
    ):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        self._name = name
        self._level = self.LEVELS.get(level.upper(), logging.INFO)
        self._log_dir = Path(log_dir) if log_dir else Path('logs')
        self._console_output = console_output
        self._file_output = file_output
        
        self._logger = logging.getLogger(name)
        self._logger.setLevel(self._level)
        self._logger.handlers.clear()
        
        self._log_queue: queue.Queue = queue.Queue()
        self._callbacks: List[Callable] = []
        self._history: List[LogRecord] = []
        self._max_history = 1000
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        if self._console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self._level)
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)
        
        if self._file_output:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            log_file = self._log_dir / f'{self._name}_{datetime.now().strftime("%Y%m%d")}.log'
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(self._level)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
    
    def _add_to_history(self, level: str, module: str, message: str, extra: Dict = None):
        record = LogRecord(
            timestamp=datetime.now(),
            level=level,
            module=module,
            message=message,
            extra=extra
        )
        
        self._history.append(record)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        
        for callback in self._callbacks:
            try:
                callback(record)
            except Exception:
                pass
    
    def debug(self, message: str, module: str = 'Main', **kwargs):
        self._logger.debug(f'[{module}] {message}')
        self._add_to_history('DEBUG', module, message, kwargs)
    
    def info(self, message: str, module: str = 'Main', **kwargs):
        self._logger.info(f'[{module}] {message}')
        self._add_to_history('INFO', module, message, kwargs)
    
    def warning(self, message: str, module: str = 'Main', **kwargs):
        self._logger.warning(f'[{module}] {message}')
        self._add_to_history('WARNING', module, message, kwargs)
    
    def error(self, message: str, module: str = 'Main', **kwargs):
        self._logger.error(f'[{module}] {message}')
        self._add_to_history('ERROR', module, message, kwargs)
    
    def critical(self, message: str, module: str = 'Main', **kwargs):
        self._logger.critical(f'[{module}] {message}')
        self._add_to_history('CRITICAL', module, message, kwargs)
    
    def exception(self, message: str, module: str = 'Main', **kwargs):
        self._logger.exception(f'[{module}] {message}')
        self._add_to_history('ERROR', module, message, kwargs)
    
    def add_callback(self, callback: Callable[[LogRecord], None]):
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def get_history(self, level: Optional[str] = None, limit: int = 100) -> List[LogRecord]:
        history = self._history.copy()
        
        if level:
            history = [r for r in history if r.level == level]
        
        return history[-limit:]
    
    def clear_history(self):
        self._history.clear()
    
    def set_level(self, level: str):
        self._level = self.LEVELS.get(level.upper(), logging.INFO)
        self._logger.setLevel(self._level)
        for handler in self._logger.handlers:
            handler.setLevel(self._level)
    
    @property
    def level(self) -> str:
        return logging.getLevelName(self._level)


logger = Logger()
