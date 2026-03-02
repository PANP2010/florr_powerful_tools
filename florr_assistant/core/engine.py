"""
Engine Manager - 核心引擎管理器
管理所有模块的生命周期和协调运行
"""

import asyncio
import threading
from typing import Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass
import time


class EngineState(Enum):
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    PAUSING = "pausing"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ModuleInfo:
    name: str
    module: object
    priority: int
    enabled: bool
    state: EngineState


class Engine:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        self._modules: Dict[str, ModuleInfo] = {}
        self._state = EngineState.IDLE
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._running = False
        self._callbacks: Dict[str, List[Callable]] = {
            'on_start': [],
            'on_stop': [],
            'on_pause': [],
            'on_resume': [],
            'on_error': [],
            'on_module_change': [],
        }
        self._stats = {
            'start_time': None,
            'run_time': 0,
            'modules_run': 0,
            'errors': 0,
        }
    
    @property
    def state(self) -> EngineState:
        return self._state
    
    @property
    def is_running(self) -> bool:
        return self._state == EngineState.RUNNING
    
    @property
    def is_paused(self) -> bool:
        return self._state == EngineState.PAUSED
    
    def register_module(self, name: str, module: object, priority: int = 0) -> bool:
        if name in self._modules:
            return False
        
        self._modules[name] = ModuleInfo(
            name=name,
            module=module,
            priority=priority,
            enabled=True,
            state=EngineState.IDLE
        )
        self._notify_callbacks('on_module_change', name, 'registered')
        return True
    
    def unregister_module(self, name: str) -> bool:
        if name not in self._modules:
            return False
        
        if self._modules[name].state == EngineState.RUNNING:
            self.stop_module(name)
        
        del self._modules[name]
        self._notify_callbacks('on_module_change', name, 'unregistered')
        return True
    
    def enable_module(self, name: str) -> bool:
        if name not in self._modules:
            return False
        self._modules[name].enabled = True
        self._notify_callbacks('on_module_change', name, 'enabled')
        return True
    
    def disable_module(self, name: str) -> bool:
        if name not in self._modules:
            return False
        self._modules[name].enabled = False
        self._notify_callbacks('on_module_change', name, 'disabled')
        return True
    
    def get_module(self, name: str) -> Optional[object]:
        if name in self._modules:
            return self._modules[name].module
        return None
    
    def get_all_modules(self) -> Dict[str, ModuleInfo]:
        return self._modules.copy()
    
    def start_module(self, name: str) -> bool:
        if name not in self._modules:
            return False
        
        module_info = self._modules[name]
        if not module_info.enabled:
            return False
        
        try:
            module_info.state = EngineState.STARTING
            if hasattr(module_info.module, 'start'):
                if asyncio.iscoroutinefunction(module_info.module.start):
                    asyncio.run_coroutine_threadsafe(
                        module_info.module.start(),
                        self._event_loop
                    )
                else:
                    module_info.module.start()
            module_info.state = EngineState.RUNNING
            self._stats['modules_run'] += 1
            return True
        except Exception as e:
            module_info.state = EngineState.ERROR
            self._stats['errors'] += 1
            self._notify_callbacks('on_error', name, str(e))
            return False
    
    def stop_module(self, name: str) -> bool:
        if name not in self._modules:
            return False
        
        module_info = self._modules[name]
        try:
            module_info.state = EngineState.STOPPING
            if hasattr(module_info.module, 'stop'):
                if asyncio.iscoroutinefunction(module_info.module.stop):
                    asyncio.run_coroutine_threadsafe(
                        module_info.module.stop(),
                        self._event_loop
                    )
                else:
                    module_info.module.stop()
            module_info.state = EngineState.STOPPED
            return True
        except Exception as e:
            module_info.state = EngineState.ERROR
            self._notify_callbacks('on_error', name, str(e))
            return False
    
    def pause_module(self, name: str) -> bool:
        if name not in self._modules:
            return False
        
        module_info = self._modules[name]
        if module_info.state != EngineState.RUNNING:
            return False
        
        try:
            module_info.state = EngineState.PAUSING
            if hasattr(module_info.module, 'pause'):
                module_info.module.pause()
            module_info.state = EngineState.PAUSED
            return True
        except Exception as e:
            module_info.state = EngineState.ERROR
            self._notify_callbacks('on_error', name, str(e))
            return False
    
    def resume_module(self, name: str) -> bool:
        if name not in self._modules:
            return False
        
        module_info = self._modules[name]
        if module_info.state != EngineState.PAUSED:
            return False
        
        try:
            if hasattr(module_info.module, 'resume'):
                module_info.module.resume()
            module_info.state = EngineState.RUNNING
            return True
        except Exception as e:
            module_info.state = EngineState.ERROR
            self._notify_callbacks('on_error', name, str(e))
            return False
    
    def start_all(self) -> bool:
        if self._state != EngineState.IDLE and self._state != EngineState.STOPPED:
            return False
        
        self._state = EngineState.STARTING
        self._stats['start_time'] = time.time()
        
        sorted_modules = sorted(
            self._modules.items(),
            key=lambda x: x[1].priority,
            reverse=True
        )
        
        success = True
        for name, module_info in sorted_modules:
            if module_info.enabled:
                if not self.start_module(name):
                    success = False
        
        self._state = EngineState.RUNNING if success else EngineState.ERROR
        self._notify_callbacks('on_start')
        return success
    
    def stop_all(self) -> bool:
        if self._state == EngineState.STOPPED or self._state == EngineState.IDLE:
            return False
        
        self._state = EngineState.STOPPING
        
        for name in list(self._modules.keys()):
            self.stop_module(name)
        
        self._stats['run_time'] += time.time() - self._stats['start_time']
        self._state = EngineState.STOPPED
        self._notify_callbacks('on_stop')
        return True
    
    def pause_all(self) -> bool:
        if self._state != EngineState.RUNNING:
            return False
        
        for name in self._modules:
            self.pause_module(name)
        
        self._state = EngineState.PAUSED
        self._notify_callbacks('on_pause')
        return True
    
    def resume_all(self) -> bool:
        if self._state != EngineState.PAUSED:
            return False
        
        for name in self._modules:
            self.resume_module(name)
        
        self._state = EngineState.RUNNING
        self._notify_callbacks('on_resume')
        return True
    
    def add_callback(self, event: str, callback: Callable) -> bool:
        if event not in self._callbacks:
            return False
        self._callbacks[event].append(callback)
        return True
    
    def remove_callback(self, event: str, callback: Callable) -> bool:
        if event not in self._callbacks:
            return False
        if callback in self._callbacks[event]:
            self._callbacks[event].remove(callback)
            return True
        return False
    
    def _notify_callbacks(self, event: str, *args, **kwargs):
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception:
                    pass
    
    def get_stats(self) -> dict:
        stats = self._stats.copy()
        if stats['start_time']:
            stats['current_run_time'] = time.time() - stats['start_time']
        return stats
    
    def get_module_states(self) -> Dict[str, EngineState]:
        return {name: info.state for name, info in self._modules.items()}
