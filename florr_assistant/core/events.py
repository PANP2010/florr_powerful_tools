"""
Event Bus - 事件总线
支持发布订阅模式，模块间解耦通信
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import threading
import queue
from enum import Enum


class EventType(Enum):
    SYSTEM = 'system'
    MODULE = 'module'
    UI = 'ui'
    GAME = 'game'
    ERROR = 'error'


@dataclass
class Event:
    name: str
    event_type: EventType
    data: Any = None
    source: str = 'unknown'
    timestamp: datetime = field(default_factory=datetime.now)
    handled: bool = False
    
    def mark_handled(self):
        self.handled = True


class EventBus:
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
        self._subscribers: Dict[str, List[Callable]] = {}
        self._type_subscribers: Dict[EventType, List[Callable]] = {}
        self._event_queue: queue.Queue = queue.Queue()
        self._processing = False
        self._process_thread: Optional[threading.Thread] = None
        self._history: List[Event] = []
        self._max_history = 100
    
    def subscribe(self, event_name: str, callback: Callable[[Event], None]) -> bool:
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        
        if callback not in self._subscribers[event_name]:
            self._subscribers[event_name].append(callback)
            return True
        return False
    
    def unsubscribe(self, event_name: str, callback: Callable) -> bool:
        if event_name in self._subscribers and callback in self._subscribers[event_name]:
            self._subscribers[event_name].remove(callback)
            return True
        return False
    
    def subscribe_type(self, event_type: EventType, callback: Callable[[Event], None]) -> bool:
        if event_type not in self._type_subscribers:
            self._type_subscribers[event_type] = []
        
        if callback not in self._type_subscribers[event_type]:
            self._type_subscribers[event_type].append(callback)
            return True
        return False
    
    def unsubscribe_type(self, event_type: EventType, callback: Callable) -> bool:
        if event_type in self._type_subscribers and callback in self._type_subscribers[event_type]:
            self._type_subscribers[event_type].remove(callback)
            return True
        return False
    
    def publish(
        self,
        event_name: str,
        event_type: EventType = EventType.SYSTEM,
        data: Any = None,
        source: str = 'unknown',
        async_process: bool = True
    ) -> Event:
        event = Event(
            name=event_name,
            event_type=event_type,
            data=data,
            source=source
        )
        
        if async_process:
            self._event_queue.put(event)
            if not self._processing:
                self._start_processing()
        else:
            self._process_event(event)
        
        return event
    
    def _start_processing(self):
        if self._processing:
            return
        
        self._processing = True
        
        def _process():
            while self._processing:
                try:
                    event = self._event_queue.get(timeout=0.1)
                    self._process_event(event)
                except queue.Empty:
                    continue
        
        self._process_thread = threading.Thread(target=_process, daemon=True)
        self._process_thread.start()
    
    def stop_processing(self):
        self._processing = False
        if self._process_thread:
            self._process_thread.join(timeout=1)
            self._process_thread = None
    
    def _process_event(self, event: Event):
        self._add_to_history(event)
        
        if event.name in self._subscribers:
            for callback in self._subscribers[event.name]:
                try:
                    callback(event)
                    if event.handled:
                        break
                except Exception:
                    pass
        
        if not event.handled and event.event_type in self._type_subscribers:
            for callback in self._type_subscribers[event.event_type]:
                try:
                    callback(event)
                    if event.handled:
                        break
                except Exception:
                    pass
    
    def _add_to_history(self, event: Event):
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)
    
    def get_history(self, event_type: Optional[EventType] = None, limit: int = 50) -> List[Event]:
        history = self._history.copy()
        
        if event_type:
            history = [e for e in history if e.event_type == event_type]
        
        return history[-limit:]
    
    def clear_history(self):
        self._history.clear()
    
    def emit(self, event_name: str, **kwargs):
        return self.publish(event_name, **kwargs)
    
    def on(self, event_name: str):
        def decorator(callback: Callable):
            self.subscribe(event_name, callback)
            return callback
        return decorator


event_bus = EventBus()
