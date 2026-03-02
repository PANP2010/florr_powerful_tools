"""
Target Selector - 目标选择器
智能选择攻击目标
"""

import os
import time
import math
from typing import Optional, Dict, Any, List, Tuple
import numpy as np

from ..base import BaseModule, ModuleState


class TargetSelector(BaseModule):
    name = 'target_selector'
    version = '1.0.0'
    description = '目标选择器'
    priority = 80
    dependencies = []
    
    MOB_TYPES = {
        'ladybug': {'priority': 1, 'danger': 0.1},
        'bee': {'priority': 2, 'danger': 0.3},
        'hornet': {'priority': 3, 'danger': 0.5},
        'spider': {'priority': 4, 'danger': 0.6},
        'scorpion': {'priority': 5, 'danger': 0.7},
        'jellyfish': {'priority': 4, 'danger': 0.5},
        'starfish': {'priority': 3, 'danger': 0.4},
        'crab': {'priority': 3, 'danger': 0.4},
        'sandstorm': {'priority': 10, 'danger': 0.9},
        'queen_ant': {'priority': 6, 'danger': 0.8},
        'centipede': {'priority': 4, 'danger': 0.5},
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        self._model = None
        self._model_path = self.get_config('model_path', 'models/mob_detector.pt')
        self._check_interval = self.get_config('check_interval', 0.2)
        self._target_priority = self.get_config('target_priority', 'nearest')
        self._avoid_danger = self.get_config('avoid_danger', True)
        
        self._current_targets: List[Dict[str, Any]] = []
        self._selected_target: Optional[Dict[str, Any]] = None
        self._detection_count = 0
    
    def _on_start(self):
        self._load_model()
        self._log('目标选择器已启动')
    
    def _on_stop(self):
        self._model = None
        self._log('目标选择器已停止')
    
    def _on_tick(self):
        try:
            from ...core.platform import PlatformManager
            platform = PlatformManager()
            
            screenshot = platform.capture_screen()
            if screenshot is None:
                time.sleep(self._check_interval)
                return
            
            mobs = self._detect_mobs(screenshot)
            
            if mobs:
                self._current_targets = mobs
                self._selected_target = self._select_target(mobs)
                self._detection_count += 1
                
                from ...core.events import EventBus, EventType
                event_bus = EventBus()
                event_bus.publish(
                    'mobs.detected',
                    event_type=EventType.GAME,
                    data={
                        'mobs': mobs,
                        'selected': self._selected_target
                    },
                    source='target_selector'
                )
            else:
                self._current_targets = []
                self._selected_target = None
            
            time.sleep(self._check_interval)
            
        except Exception as e:
            self._log(f'检测错误: {e}', level='ERROR')
            time.sleep(1)
    
    def _load_model(self):
        try:
            from ultralytics import YOLO
            
            model_path = self._resolve_model_path()
            if os.path.exists(model_path):
                self._model = YOLO(model_path)
                self._log(f'模型加载成功: {model_path}')
            else:
                self._log(f'模型文件不存在: {model_path}', level='WARNING')
        except ImportError:
            self._log('ultralytics未安装，使用颜色检测', level='WARNING')
        except Exception as e:
            self._log(f'模型加载失败: {e}', level='ERROR')
    
    def _resolve_model_path(self) -> str:
        if os.path.isabs(self._model_path):
            return self._model_path
        
        root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(root_path, self._model_path)
    
    def _detect_mobs(self, image: np.ndarray) -> List[Dict[str, Any]]:
        mobs = []
        
        if self._model is not None:
            mobs = self._detect_with_model(image)
        else:
            mobs = self._detect_with_color(image)
        
        return mobs
    
    def _detect_with_model(self, image: np.ndarray) -> List[Dict[str, Any]]:
        mobs = []
        
        try:
            results = self._model(image, verbose=False)
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        confidence = float(box.conf[0])
                        if confidence >= 0.5:
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            class_id = int(box.cls[0])
                            class_name = result.names.get(class_id, 'unknown')
                            
                            mobs.append({
                                'bbox': [int(x1), int(y1), int(x2-x1), int(y2-y1)],
                                'center': (int((x1+x2)/2), int((y1+y2)/2)),
                                'confidence': confidence,
                                'class': class_name,
                                'class_id': class_id,
                                'info': self.MOB_TYPES.get(class_name.lower(), {'priority': 1, 'danger': 0.3})
                            })
        except Exception as e:
            self._log(f'YOLO检测错误: {e}', level='ERROR')
        
        return mobs
    
    def _detect_with_color(self, image: np.ndarray) -> List[Dict[str, Any]]:
        mobs = []
        
        try:
            import cv2
            
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            color_ranges = {
                'red': ([0, 100, 100], [10, 255, 255]),
                'yellow': ([20, 100, 100], [40, 255, 255]),
                'green': ([40, 100, 100], [80, 255, 255]),
                'blue': ([100, 100, 100], [130, 255, 255]),
            }
            
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            
            for color_name, (lower, upper) in color_ranges.items():
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 500:
                        x, y, bw, bh = cv2.boundingRect(contour)
                        
                        mobs.append({
                            'bbox': [x, y, bw, bh],
                            'center': (x + bw // 2, y + bh // 2),
                            'confidence': 0.5,
                            'class': color_name,
                            'class_id': 0,
                            'info': {'priority': 2, 'danger': 0.3}
                        })
        except Exception as e:
            self._log(f'颜色检测错误: {e}', level='ERROR')
        
        return mobs
    
    def _select_target(self, mobs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not mobs:
            return None
        
        from ...core.platform import PlatformManager
        platform = PlatformManager()
        screen_size = platform.get_screen_size()
        player_pos = (screen_size[0] // 2, screen_size[1] // 2)
        
        for mob in mobs:
            mob['distance'] = self._distance(mob['center'], player_pos)
        
        if self._target_priority == 'nearest':
            mobs.sort(key=lambda m: m['distance'])
        elif self._target_priority == 'highest_priority':
            mobs.sort(key=lambda m: m['info']['priority'], reverse=True)
        elif self._target_priority == 'lowest_danger':
            mobs.sort(key=lambda m: m['info']['danger'])
        
        if self._avoid_danger:
            for mob in mobs:
                if mob['info']['danger'] < 0.7:
                    return mob
            return None
        
        return mobs[0] if mobs else None
    
    def _distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
    
    def _log(self, message: str, level: str = 'INFO'):
        from ...core.logger import Logger
        logger = Logger()
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message, module='TargetSelector')
    
    def get_current_targets(self) -> List[Dict[str, Any]]:
        return self._current_targets
    
    def get_selected_target(self) -> Optional[Dict[str, Any]]:
        return self._selected_target
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'detection_count': self._detection_count,
            'current_targets': len(self._current_targets),
            'selected_target': self._selected_target
        }
