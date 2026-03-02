"""
Florr Assistant - 主应用类
整合所有模块，提供统一入口
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
import threading
import time

from .core.engine import Engine, EngineState
from .core.config import Config
from .core.logger import Logger, LogRecord
from .core.events import EventBus, Event, EventType
from .core.platform import PlatformManager, PlatformType


class FlorrAssistant:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        headless: bool = False,
    ):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        self._headless = headless
        self._running = False
        
        self._init_paths()
        
        self.config = Config(config_path)
        self.logger = Logger(
            name='FlorrAssistant',
            level=self.config.get('general.log_level', 'INFO'),
            log_dir=self.config.get('paths.logs_dir', 'logs'),
        )
        self.event_bus = EventBus()
        self.platform = PlatformManager()
        self.engine = Engine()
        
        self._ui = None
        self._modules: Dict[str, Any] = {}
        
        self._setup_event_handlers()
        self._log_startup_info()
    
    def _init_paths(self):
        self._root_path = Path(__file__).parent.parent
        
        sys.path.insert(0, str(self._root_path))
        
        for dir_name in ['logs', 'config', 'models']:
            dir_path = self._root_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _setup_event_handlers(self):
        self.event_bus.subscribe_type(EventType.ERROR, self._on_error_event)
        self.event_bus.subscribe('module.started', self._on_module_started)
        self.event_bus.subscribe('module.stopped', self._on_module_stopped)
        
        self.engine.add_callback('on_error', self._on_engine_error)
        self.engine.add_callback('on_module_change', self._on_module_change)
    
    def _log_startup_info(self):
        self.logger.info('=' * 50, 'Main')
        self.logger.info('Florr Assistant Starting...', 'Main')
        self.logger.info(f'Platform: {self.platform.type.value}', 'Main')
        self.logger.info(f'Python: {sys.version.split()[0]}', 'Main')
        self.logger.info(f'Root Path: {self._root_path}', 'Main')
        self.logger.info('=' * 50, 'Main')
        
        self._register_default_modules()
    
    def _register_default_modules(self):
        self.logger.info('Registering modules...', 'Main')
        
        try:
            from .modules.afk.detector import AFKDetector
            from .modules.afk.responder import AFKResponder
            from .modules.pathing.map_classifier import MapClassifier
            from .modules.pathing.navigator import Navigator
            from .modules.combat.target_selector import TargetSelector
            from .modules.combat.fighter import Fighter
            from .modules.stats.collector import StatsCollector
            
            self.register_module('afk_detector', AFKDetector)
            self.register_module('afk_responder', AFKResponder)
            self.register_module('map_classifier', MapClassifier)
            self.register_module('navigator', Navigator)
            self.register_module('target_selector', TargetSelector)
            self.register_module('fighter', Fighter)
            self.register_module('stats_collector', StatsCollector)
            
            self.logger.info(f'Registered {len(self._modules)} modules', 'Main')
            
        except Exception as e:
            self.logger.error(f'Failed to register modules: {e}', 'Main')
    
    def register_module(self, name: str, module_class: type, config: Optional[Dict] = None) -> bool:
        if name in self._modules:
            self.logger.warning(f'Module {name} already registered', 'Main')
            return False
        
        try:
            module_config = config or self.config.get_module_config(name)
            module = module_class(config=module_config)
            
            self._modules[name] = module
            self.engine.register_module(name, module, module.priority)
            
            self.logger.info(f'Module registered: {name} (priority: {module.priority})', 'Main')
            return True
        except Exception as e:
            self.logger.error(f'Failed to register module {name}: {e}', 'Main')
            return False
    
    def unregister_module(self, name: str) -> bool:
        if name not in self._modules:
            return False
        
        if self.engine.is_running:
            self.engine.stop_module(name)
        
        self.engine.unregister_module(name)
        del self._modules[name]
        
        self.logger.info(f'Module unregistered: {name}', 'Main')
        return True
    
    def get_module(self, name: str) -> Optional[Any]:
        return self._modules.get(name)
    
    def start_module(self, name: str) -> bool:
        if name not in self._modules:
            self.logger.error(f'Module {name} not found', 'Main')
            return False
        
        result = self.engine.start_module(name)
        if result:
            self.logger.info(f'Module started: {name}', 'Main')
        else:
            self.logger.error(f'Failed to start module: {name}', 'Main')
        return result
    
    def stop_module(self, name: str) -> bool:
        if name not in self._modules:
            return False
        
        result = self.engine.stop_module(name)
        if result:
            self.logger.info(f'Module stopped: {name}', 'Main')
        return result
    
    def start_all(self) -> bool:
        self.logger.info('Starting all modules...', 'Main')
        result = self.engine.start_all()
        if result:
            self._running = True
            self.logger.info('All modules started successfully', 'Main')
        else:
            self.logger.error('Failed to start all modules', 'Main')
        return result
    
    def stop_all(self) -> bool:
        self.logger.info('Stopping all modules...', 'Main')
        result = self.engine.stop_all()
        if result:
            self._running = False
            self.logger.info('All modules stopped', 'Main')
        return result
    
    def pause_all(self) -> bool:
        return self.engine.pause_all()
    
    def resume_all(self) -> bool:
        return self.engine.resume_all()
    
    def run(self):
        if self._headless:
            self._run_headless()
        else:
            self._run_with_ui()
    
    def _run_headless(self):
        self.logger.info('Running in headless mode', 'Main')
        self.start_all()
        
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info('Received interrupt signal', 'Main')
            self.stop_all()
    
    def _run_with_ui(self):
        try:
            from PyQt5.QtWidgets import QApplication
            from .ui.overlay_window import ModernOverlayWindow
            
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            self._ui = ModernOverlayWindow(self)
            self._ui.run()
        except ImportError as e:
            self.logger.error(f'Failed to load UI: {e}', 'Main')
            self.logger.info('Falling back to headless mode', 'Main')
            self._run_headless()
    
    def _on_error_event(self, event: Event):
        self.logger.error(f'Error event: {event.data}', 'EventBus')
    
    def _on_module_started(self, event: Event):
        self.logger.info(f'Module started: {event.data}', 'EventBus')
    
    def _on_module_stopped(self, event: Event):
        self.logger.info(f'Module stopped: {event.data}', 'EventBus')
    
    def _on_engine_error(self, module_name: str, error: str):
        self.logger.error(f'Engine error in {module_name}: {error}', 'Engine')
    
    def _on_module_change(self, module_name: str, action: str):
        self.logger.debug(f'Module {module_name}: {action}', 'Engine')
    
    @property
    def is_running(self) -> bool:
        return self._running
    
    def get_status(self) -> Dict[str, Any]:
        return {
            'running': self._running,
            'engine_state': self.engine.state.value,
            'modules': {
                name: {
                    'state': self.engine.get_module_states().get(name, 'unknown'),
                    'info': module.get_info() if hasattr(module, 'get_info') else {}
                }
                for name, module in self._modules.items()
            },
            'platform': self.platform.info,
            'stats': self.engine.get_stats(),
        }
    
    def shutdown(self):
        self.logger.info('Shutting down...', 'Main')
        self.stop_all()
        self.event_bus.stop_processing()
        self.logger.info('Shutdown complete', 'Main')
