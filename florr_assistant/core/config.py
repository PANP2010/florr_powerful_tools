"""
Config Manager - 配置管理器
支持YAML配置文件，热重载，环境变量
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass, field
import threading
import time


@dataclass
class ConfigSchema:
    general: Dict[str, Any] = field(default_factory=lambda: {
        'language': 'zh_CN',
        'theme': 'dark',
        'auto_start': False,
        'minimize_to_tray': True,
    })
    
    modules: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'afk': {
            'enabled': True,
            'check_interval': 0.5,
            'auto_respond': True,
            'llm_enabled': False,
            'llm_provider': 'ollama',
            'llm_model': 'qwen2.5:14b',
        },
        'pathing': {
            'enabled': True,
            'target_map': 'ocean',
            'auto_navigate': False,
            'avoid_danger': True,
        },
        'combat': {
            'enabled': True,
            'target_priority': 'nearest',
            'auto_dodge': True,
            'sandstorm_avoid': True,
        },
        'stats': {
            'enabled': True,
            'track_petals': True,
            'track_efficiency': True,
            'export_format': 'json',
        },
    })
    
    platform: Dict[str, Any] = field(default_factory=lambda: {
        'screen_capture': 'auto',
        'input_method': 'pyautogui',
        'capture_fps': 30,
        'game_window': 'florr.io',
    })
    
    ui: Dict[str, Any] = field(default_factory=lambda: {
        'window_width': 800,
        'window_height': 600,
        'opacity': 0.95,
        'always_on_top': False,
        'show_notifications': True,
    })
    
    paths: Dict[str, str] = field(default_factory=lambda: {
        'models_dir': 'models',
        'logs_dir': 'logs',
        'screenshots_dir': 'assets/screenshots',
    })


class Config:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        self._config_path = config_path
        self._config: Dict[str, Any] = {}
        self._defaults = ConfigSchema()
        self._callbacks: Dict[str, list] = {}
        self._last_modified = 0
        self._watch_thread: Optional[threading.Thread] = None
        self._watching = False
        
        self._load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            'general': self._defaults.general,
            'modules': self._defaults.modules,
            'platform': self._defaults.platform,
            'ui': self._defaults.ui,
            'paths': self._defaults.paths,
        }
    
    def _find_config_file(self) -> Optional[Path]:
        search_paths = [
            Path('config/default.yaml'),
            Path('config/default.yml'),
            Path('config/config.yaml'),
            Path('config.json'),
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        return None
    
    def _load_config(self):
        if self._config_path:
            config_file = Path(self._config_path)
        else:
            config_file = self._find_config_file()
        
        default_config = self._get_default_config()
        
        if config_file and config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    if config_file.suffix in ['.yaml', '.yml']:
                        loaded_config = yaml.safe_load(f) or {}
                    else:
                        loaded_config = json.load(f)
                
                self._config = self._deep_merge(default_config, loaded_config)
                self._last_modified = config_file.stat().st_mtime
            except Exception:
                self._config = default_config
        else:
            self._config = default_config
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, save: bool = True):
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        
        if save:
            self.save()
        
        self._notify_change(key, value)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        return self._config.get(section, {})
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        return self._config.get('modules', {}).get(module_name, {})
    
    def save(self, path: Optional[str] = None):
        save_path = Path(path) if path else (Path(self._config_path) if self._config_path else Path('config/default.yaml'))
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            if save_path.suffix in ['.yaml', '.yml']:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
            else:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def reload(self):
        self._load_config()
        self._notify_change('*', self._config)
    
    def watch_changes(self, interval: float = 1.0):
        if self._watching:
            return
        
        self._watching = True
        
        def _watch():
            while self._watching:
                if self._config_path:
                    config_file = Path(self._config_path)
                    if config_file.exists():
                        modified = config_file.stat().st_mtime
                        if modified > self._last_modified:
                            self.reload()
                            self._last_modified = modified
                time.sleep(interval)
        
        self._watch_thread = threading.Thread(target=_watch, daemon=True)
        self._watch_thread.start()
    
    def stop_watching(self):
        self._watching = False
        if self._watch_thread:
            self._watch_thread.join(timeout=2)
            self._watch_thread = None
    
    def on_change(self, key: str, callback: Callable):
        if key not in self._callbacks:
            self._callbacks[key] = []
        self._callbacks[key].append(callback)
    
    def _notify_change(self, key: str, value: Any):
        if key in self._callbacks:
            for callback in self._callbacks[key]:
                try:
                    callback(key, value)
                except Exception:
                    pass
        
        if '*' in self._callbacks:
            for callback in self._callbacks['*']:
                try:
                    callback(key, value)
                except Exception:
                    pass
    
    def reset_to_defaults(self):
        self._config = self._get_default_config()
        self.save()
        self._notify_change('*', self._config)
    
    @property
    def all(self) -> Dict[str, Any]:
        return self._config.copy()
