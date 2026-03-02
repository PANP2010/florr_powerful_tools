"""
Platform Manager - 平台适配管理器
自动检测操作系统并提供对应的平台实现
"""

import platform
import sys
import threading
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np


class PlatformType(Enum):
    WINDOWS = 'windows'
    MACOS = 'macos'
    LINUX = 'linux'
    UNKNOWN = 'unknown'


@dataclass
class ScreenInfo:
    width: int
    height: int
    scale: float = 1.0
    primary: bool = True


class PlatformBase(ABC):
    @abstractmethod
    def get_platform_type(self) -> PlatformType:
        pass
    
    @abstractmethod
    def get_screen_size(self) -> Tuple[int, int]:
        pass
    
    @abstractmethod
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        pass
    
    @abstractmethod
    def capture_window(self, window_title: str) -> Optional[np.ndarray]:
        pass
    
    @abstractmethod
    def mouse_move(self, x: int, y: int, smooth: bool = True):
        pass
    
    @abstractmethod
    def mouse_click(self, x: int, y: int, button: str = 'left', clicks: int = 1):
        pass
    
    @abstractmethod
    def mouse_drag(self, start: Tuple[int, int], end: Tuple[int, int], duration: float = 0.5):
        pass
    
    @abstractmethod
    def key_press(self, key: str, modifiers: Optional[list] = None):
        pass
    
    @abstractmethod
    def key_type(self, text: str, interval: float = 0.05):
        pass
    
    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        pass
    
    @abstractmethod
    def find_window(self, title: str) -> Optional[int]:
        pass
    
    @abstractmethod
    def get_window_rect(self, window_id: int) -> Optional[Tuple[int, int, int, int]]:
        pass
    
    @abstractmethod
    def bring_window_to_front(self, window_id: int):
        pass
    
    def get_platform_info(self) -> Dict[str, Any]:
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
        }


class CrossPlatformBase(PlatformBase):
    def __init__(self):
        import pyautogui
        self._pyautogui = pyautogui
        self._pyautogui.FAILSAFE = True
        self._pyautogui.PAUSE = 0.01
    
    def get_platform_type(self) -> PlatformType:
        system = platform.system().lower()
        if system == 'windows':
            return PlatformType.WINDOWS
        elif system == 'darwin':
            return PlatformType.MACOS
        elif system == 'linux':
            return PlatformType.LINUX
        return PlatformType.UNKNOWN
    
    def get_screen_size(self) -> Tuple[int, int]:
        return self._pyautogui.size()
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        import cv2
        
        if region:
            x, y, w, h = region
            screenshot = self._pyautogui.screenshot(region=(x, y, w, h))
        else:
            screenshot = self._pyautogui.screenshot()
        
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def capture_window(self, window_title: str) -> Optional[np.ndarray]:
        window_id = self.find_window(window_title)
        if window_id is None:
            return None
        
        rect = self.get_window_rect(window_id)
        if rect is None:
            return None
        
        return self.capture_screen(region=rect)
    
    def mouse_move(self, x: int, y: int, smooth: bool = True):
        if smooth:
            self._pyautogui.moveTo(x, y, duration=0.2)
        else:
            self._pyautogui.moveTo(x, y)
    
    def mouse_click(self, x: int, y: int, button: str = 'left', clicks: int = 1):
        self._pyautogui.click(x, y, clicks=clicks, button=button)
    
    def mouse_drag(self, start: Tuple[int, int], end: Tuple[int, int], duration: float = 0.5):
        self._pyautogui.moveTo(start[0], start[1])
        self._pyautogui.drag(end[0] - start[0], end[1] - start[1], duration=duration)
    
    def key_press(self, key: str, modifiers: Optional[list] = None):
        if modifiers:
            self._pyautogui.hotkey(*modifiers, key)
        else:
            self._pyautogui.press(key)
    
    def key_type(self, text: str, interval: float = 0.05):
        self._pyautogui.write(text, interval=interval)
    
    def get_mouse_position(self) -> Tuple[int, int]:
        return self._pyautogui.position()
    
    def find_window(self, title: str) -> Optional[int]:
        return None
    
    def get_window_rect(self, window_id: int) -> Optional[Tuple[int, int, int, int]]:
        return None
    
    def bring_window_to_front(self, window_id: int):
        pass


class WindowsPlatform(CrossPlatformBase):
    def __init__(self):
        super().__init__()
        try:
            import win32gui
            import win32con
            self._win32gui = win32gui
            self._win32con = win32con
            self._has_win32 = True
        except ImportError:
            self._has_win32 = False
    
    def find_window(self, title: str) -> Optional[int]:
        if not self._has_win32:
            return None
        
        try:
            return self._win32gui.FindWindow(None, title)
        except Exception:
            return None
    
    def get_window_rect(self, window_id: int) -> Optional[Tuple[int, int, int, int]]:
        if not self._has_win32:
            return None
        
        try:
            return self._win32gui.GetWindowRect(window_id)
        except Exception:
            return None
    
    def bring_window_to_front(self, window_id: int):
        if not self._has_win32:
            return
        
        try:
            self._win32gui.ShowWindow(window_id, self._win32con.SW_RESTORE)
            self._win32gui.SetForegroundWindow(window_id)
        except Exception:
            pass


class MacOSPlatform(CrossPlatformBase):
    def __init__(self):
        super().__init__()
        try:
            from AppKit import NSWorkspace
            self._workspace = NSWorkspace.sharedWorkspace()
            self._has_appkit = True
        except ImportError:
            self._has_appkit = False
    
    def find_window(self, title: str) -> Optional[int]:
        return None
    
    def get_window_rect(self, window_id: int) -> Optional[Tuple[int, int, int, int]]:
        return None
    
    def bring_window_to_front(self, window_id: int):
        pass


class LinuxPlatform(CrossPlatformBase):
    def __init__(self):
        super().__init__()
        try:
            import Xlib.display
            self._display = Xlib.display.Display()
            self._has_xlib = True
        except ImportError:
            self._has_xlib = False
    
    def find_window(self, title: str) -> Optional[int]:
        return None
    
    def get_window_rect(self, window_id: int) -> Optional[Tuple[int, int, int, int]]:
        return None
    
    def bring_window_to_front(self, window_id: int):
        pass


class PlatformManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if object.__getattribute__(self, '_initialized') if hasattr(self, '_initialized') else False:
            return
        
        self._initialized = True
        self._platform = self._detect_platform()
        self._info = self._platform.get_platform_info()
    
    def _detect_platform(self) -> 'PlatformBase':
        system = platform.system().lower()
        
        if system == 'windows':
            return WindowsPlatform()
        elif system == 'darwin':
            return MacOSPlatform()
        elif system == 'linux':
            return LinuxPlatform()
        else:
            return CrossPlatformBase()
    
    @property
    def platform(self) -> 'PlatformBase':
        return self._platform
    
    @property
    def type(self) -> 'PlatformType':
        return self._platform.get_platform_type()
    
    @property
    def is_windows(self) -> bool:
        return self.type == PlatformType.WINDOWS
    
    @property
    def is_macos(self) -> bool:
        return self.type == PlatformType.MACOS
    
    @property
    def is_linux(self) -> bool:
        return self.type == PlatformType.LINUX
    
    @property
    def info(self) -> Dict[str, Any]:
        return self._info
    
    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, '_platform').__getattribute__(name)
        except AttributeError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
