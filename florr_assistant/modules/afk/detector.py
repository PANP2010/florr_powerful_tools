"""
AFK Detector - AFK窗口检测器
使用YOLO模型检测游戏中的AFK验证窗口
"""

import os
import time
from typing import Optional, Dict, Any, List, Tuple
import numpy as np

from ..base import BaseModule, ModuleState


class AFKDetector(BaseModule):
    name = 'afk_detector'
    version = '1.0.0'
    description = 'AFK窗口检测器'
    priority = 100
    dependencies = []
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        self._model = None
        self._model_path = self.get_config('model_path', 'models/afk-det.pt')
        self._check_interval = self.get_config('check_interval', 0.5)
        self._confidence_threshold = self.get_config('confidence_threshold', 0.7)
        self._last_detection = None
        self._detection_count = 0
    
    def _on_start(self):
        self._load_model()
        self._log('AFK检测器已启动')
    
    def _on_stop(self):
        self._model = None
        self._log('AFK检测器已停止')
    
    def _on_tick(self):
        try:
            from ...core.platform import PlatformManager
            platform = PlatformManager()
            
            screenshot = platform.capture_screen()
            if screenshot is None:
                time.sleep(self._check_interval)
                return
            
            detections = self._detect(screenshot)
            
            if detections:
                self._last_detection = {
                    'timestamp': time.time(),
                    'detections': detections
                }
                self._detection_count += 1
                
                from ...core.events import EventBus, EventType
                event_bus = EventBus()
                event_bus.publish(
                    'afk.detected',
                    event_type=EventType.GAME,
                    data={'detections': detections},
                    source='afk_detector'
                )
            
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
                self._log('将使用默认检测方法', level='WARNING')
        except ImportError:
            self._log('ultralytics未安装，AFK检测功能受限', level='WARNING')
        except Exception as e:
            self._log(f'模型加载失败: {e}', level='ERROR')
    
    def _resolve_model_path(self) -> str:
        if os.path.isabs(self._model_path):
            return self._model_path
        
        root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(root_path, self._model_path)
    
    def _detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        detections = []
        
        if self._model is not None:
            try:
                results = self._model(image, verbose=False)
                
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            confidence = float(box.conf[0])
                            if confidence >= self._confidence_threshold:
                                x1, y1, x2, y2 = box.xyxy[0].tolist()
                                class_id = int(box.cls[0])
                                class_name = result.names.get(class_id, 'unknown')
                                
                                detections.append({
                                    'bbox': [int(x1), int(y1), int(x2-x1), int(y2-y1)],
                                    'confidence': confidence,
                                    'class': class_name,
                                    'class_id': class_id
                                })
            except Exception as e:
                self._log(f'YOLO检测错误: {e}', level='ERROR')
        
        return detections
    
    def _log(self, message: str, level: str = 'INFO'):
        from ...core.logger import Logger
        logger = Logger()
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message, module='AFKDetector')
    
    def get_last_detection(self) -> Optional[Dict[str, Any]]:
        return self._last_detection
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'detection_count': self._detection_count,
            'last_detection': self._last_detection
        }
