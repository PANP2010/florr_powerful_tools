"""
Base Module - 模块基类
所有功能模块的抽象基类
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable, List
from enum import Enum
from dataclasses import dataclass
import threading
import time


class ModuleState(Enum):
    IDLE = 'idle'
    STARTING = 'starting'
    RUNNING = 'running'
    PAUSED = 'paused'
    STOPPING = 'stopping'
    STOPPED = 'stopped'
    ERROR = 'error'


@dataclass
class ModuleStats:
    start_time: Optional[float] = None
    run_time: float = 0
    cycles: int = 0
    errors: int = 0
    last_error: Optional[str] = None


class BaseModule(ABC):
    name: str = 'base'
    version: str = '1.0.0'
    description: str = 'Base module'
    priority: int = 0
    dependencies: List[str] = []
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = config or {}
        self._state = ModuleState.IDLE
        self._stats = ModuleStats()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._paused = False
        self._callbacks: Dict[str, List[Callable]] = {
            'on_start': [],
            'on_stop': [],
            'on_pause': [],
            'on_resume': [],
            'on_error': [],
            'on_state_change': [],
        }
        self._lock = threading.Lock()
    
    @property
    def state(self) -> ModuleState:
        return self._state
    
    @property
    def is_running(self) -> bool:
        return self._state == ModuleState.RUNNING
    
    @property
    def is_paused(self) -> bool:
        return self._state == ModuleState.PAUSED
    
    @property
    def stats(self) -> ModuleStats:
        return self._stats
    
    def _set_state(self, state: ModuleState):
        old_state = self._state
        self._state = state
        self._notify_callbacks('on_state_change', old_state, state)
    
    def start(self) -> bool:
        if self._state not in [ModuleState.IDLE, ModuleState.STOPPED]:
            return False
        
        self._set_state(ModuleState.STARTING)
        
        try:
            self._on_start()
            self._running = True
            self._paused = False
            self._stats.start_time = time.time()
            
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            
            self._set_state(ModuleState.RUNNING)
            self._notify_callbacks('on_start')
            return True
        except Exception as e:
            self._set_state(ModuleState.ERROR)
            self._stats.errors += 1
            self._stats.last_error = str(e)
            self._notify_callbacks('on_error', str(e))
            return False
    
    def stop(self) -> bool:
        if self._state not in [ModuleState.RUNNING, ModuleState.PAUSED]:
            return False
        
        self._set_state(ModuleState.STOPPING)
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        
        try:
            self._on_stop()
        except Exception:
            pass
        
        if self._stats.start_time:
            self._stats.run_time += time.time() - self._stats.start_time
        
        self._set_state(ModuleState.STOPPED)
        self._notify_callbacks('on_stop')
        return True
    
    def pause(self) -> bool:
        if self._state != ModuleState.RUNNING:
            return False
        
        self._paused = True
        self._set_state(ModuleState.PAUSED)
        
        try:
            self._on_pause()
        except Exception:
            pass
        
        self._notify_callbacks('on_pause')
        return True
    
    def resume(self) -> bool:
        if self._state != ModuleState.PAUSED:
            return False
        
        self._paused = False
        self._set_state(ModuleState.RUNNING)
        
        try:
            self._on_resume()
        except Exception:
            pass
        
        self._notify_callbacks('on_resume')
        return True
    
    def _run_loop(self):
        while self._running:
            if self._paused:
                time.sleep(0.1)
                continue
            
            try:
                self._on_tick()
                self._stats.cycles += 1
            except Exception as e:
                self._stats.errors += 1
                self._stats.last_error = str(e)
                self._notify_callbacks('on_error', str(e))
    
    @abstractmethod
    def _on_start(self):
        pass
    
    @abstractmethod
    def _on_stop(self):
        pass
    
    @abstractmethod
    def _on_tick(self):
        pass
    
    def _on_pause(self):
        pass
    
    def _on_resume(self):
        pass
    
    def add_callback(self, event: str, callback: Callable) -> bool:
        if event in self._callbacks:
            self._callbacks[event].append(callback)
            return True
        return False
    
    def remove_callback(self, event: str, callback: Callable) -> bool:
        if event in self._callbacks and callback in self._callbacks[event]:
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
    
    def get_config(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)
    
    def set_config(self, key: str, value: Any):
        self._config[key] = value
    
    def get_info(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'priority': self.priority,
            'dependencies': self.dependencies,
            'state': self._state.value,
            'stats': {
                'run_time': self._stats.run_time,
                'cycles': self._stats.cycles,
                'errors': self._stats.errors,
            }
        }
