"""
Map Classifier - 地图分类器
使用多尺度模板匹配从游戏截图中识别当前地图
"""

import os
import time
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import cv2

from ..base import BaseModule, ModuleState


@dataclass
class MatchResult:
    map_name: str
    confidence: float
    top_left: Tuple[int, int]
    bottom_right: Tuple[int, int]
    scale: float
    template_size: Tuple[int, int]
    matched_size: Tuple[int, int]


class FullscreenTemplateMatcher:
    def __init__(self, maps_dir: str, default_scales: List[float] = None):
        self.maps_dir = maps_dir
        self.templates: Dict[str, np.ndarray] = {}
        self.template_info: Dict[str, Dict] = {}
        
        if default_scales is None:
            default_scales = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0]
        self.default_scales = default_scales
        
        self._load_templates()
    
    def _load_templates(self):
        if not os.path.exists(self.maps_dir):
            return
        
        for filename in os.listdir(self.maps_dir):
            if filename.endswith('.png'):
                map_name = filename.replace('.png', '')
                filepath = os.path.join(self.maps_dir, filename)
                
                template = cv2.imread(filepath, cv2.IMREAD_COLOR)
                if template is not None:
                    self.templates[map_name] = template
                    self.template_info[map_name] = {
                        'filename': filename,
                        'size': template.shape[:2][::-1],
                        'path': filepath
                    }
    
    def _multi_scale_match(self, image: np.ndarray, template: np.ndarray,
                           scales: List[float] = None,
                           threshold: float = 0.5) -> Tuple[float, Tuple[int, int], float, Tuple[int, int]]:
        if scales is None:
            scales = self.default_scales
        
        best_match_val = 0
        best_match_loc = (0, 0)
        best_scale = 1.0
        best_size = (0, 0)
        
        template_h, template_w = template.shape[:2]
        
        for scale in scales:
            new_w = int(template_w * scale)
            new_h = int(template_h * scale)
            
            if new_w < 10 or new_h < 10:
                continue
            
            if new_h > image.shape[0] or new_w > image.shape[1]:
                continue
            
            resized_template = cv2.resize(template, (new_w, new_h),
                                          interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
            
            result = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_match_val:
                best_match_val = max_val
                best_match_loc = max_loc
                best_scale = scale
                best_size = (new_w, new_h)
        
        return best_match_val, best_match_loc, best_scale, best_size
    
    def _pyramid_search(self, image: np.ndarray, template: np.ndarray,
                        coarse_scales: List[float] = None,
                        fine_scales_range: float = 0.2,
                        threshold: float = 0.5) -> Tuple[float, Tuple[int, int], float, Tuple[int, int]]:
        if coarse_scales is None:
            coarse_scales = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
        
        coarse_val, coarse_loc, coarse_scale, coarse_size = self._multi_scale_match(
            image, template, coarse_scales, threshold
        )
        
        if coarse_val < threshold:
            return coarse_val, coarse_loc, coarse_scale, coarse_size
        
        fine_scales = []
        step = 0.05
        for s in np.arange(max(0.3, coarse_scale - fine_scales_range),
                          coarse_scale + fine_scales_range + step, step):
            fine_scales.append(round(s, 2))
        
        fine_val, fine_loc, fine_scale, fine_size = self._multi_scale_match(
            image, template, fine_scales, threshold
        )
        
        if fine_val > coarse_val:
            return fine_val, fine_loc, fine_scale, fine_size
        return coarse_val, coarse_loc, coarse_scale, coarse_size
    
    def match(self, screenshot: np.ndarray, 
              scales: List[float] = None,
              use_pyramid: bool = True,
              threshold: float = 0.5,
              search_region: Tuple[int, int, int, int] = None) -> Optional[MatchResult]:
        if screenshot is None or len(self.templates) == 0:
            return None
        
        if search_region:
            x1, y1, x2, y2 = search_region
            search_image = screenshot[y1:y2, x1:x2]
            offset = (x1, y1)
        else:
            search_image = screenshot
            offset = (0, 0)
        
        best_result = None
        best_confidence = 0
        
        for map_name, template in self.templates.items():
            if use_pyramid:
                match_val, match_loc, best_scale, matched_size = self._pyramid_search(
                    search_image, template, threshold=threshold
                )
            else:
                match_val, match_loc, best_scale, matched_size = self._multi_scale_match(
                    search_image, template, scales, threshold
                )
            
            if match_val > best_confidence and match_val >= threshold:
                best_confidence = match_val
                
                top_left = (match_loc[0] + offset[0], match_loc[1] + offset[1])
                bottom_right = (top_left[0] + matched_size[0], top_left[1] + matched_size[1])
                
                best_result = MatchResult(
                    map_name=map_name,
                    confidence=match_val,
                    top_left=top_left,
                    bottom_right=bottom_right,
                    scale=best_scale,
                    template_size=self.template_info[map_name]['size'],
                    matched_size=matched_size
                )
        
        return best_result
    
    def match_all(self, screenshot: np.ndarray,
                  scales: List[float] = None,
                  use_pyramid: bool = True,
                  threshold: float = 0.5,
                  search_region: Tuple[int, int, int, int] = None) -> List[MatchResult]:
        if screenshot is None or len(self.templates) == 0:
            return []
        
        if search_region:
            x1, y1, x2, y2 = search_region
            search_image = screenshot[y1:y2, x1:x2]
            offset = (x1, y1)
        else:
            search_image = screenshot
            offset = (0, 0)
        
        results = []
        
        for map_name, template in self.templates.items():
            if use_pyramid:
                match_val, match_loc, best_scale, matched_size = self._pyramid_search(
                    search_image, template, threshold=threshold
                )
            else:
                match_val, match_loc, best_scale, matched_size = self._multi_scale_match(
                    search_image, template, scales, threshold
                )
            
            if match_val >= threshold:
                top_left = (match_loc[0] + offset[0], match_loc[1] + offset[1])
                bottom_right = (top_left[0] + matched_size[0], top_left[1] + matched_size[1])
                
                results.append(MatchResult(
                    map_name=map_name,
                    confidence=match_val,
                    top_left=top_left,
                    bottom_right=bottom_right,
                    scale=best_scale,
                    template_size=self.template_info[map_name]['size'],
                    matched_size=matched_size
                ))
        
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results
    
    def get_center(self, result: MatchResult) -> Tuple[int, int]:
        center_x = (result.top_left[0] + result.bottom_right[0]) // 2
        center_y = (result.top_left[1] + result.bottom_right[1]) // 2
        return (center_x, center_y)
    
    def get_width_height(self, result: MatchResult) -> Tuple[int, int]:
        width = result.bottom_right[0] - result.top_left[0]
        height = result.bottom_right[1] - result.top_left[1]
        return (width, height)
    
    def draw_match(self, screenshot: np.ndarray, result: MatchResult,
                   color: Tuple[int, int, int] = (0, 255, 0),
                   thickness: int = 2) -> np.ndarray:
        output = screenshot.copy()
        cv2.rectangle(output, result.top_left, result.bottom_right, color, thickness)
        
        label = f"{result.map_name}: {result.confidence:.2f} ({result.scale:.2f}x)"
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        
        label_top = (result.top_left[0], result.top_left[1] - 10)
        if label_top[1] < 20:
            label_top = (result.top_left[0], result.bottom_right[1] + 25)
        
        cv2.rectangle(output, 
                     (label_top[0], label_top[1] - label_size[1] - 5),
                     (label_top[0] + label_size[0], label_top[1] + 5),
                     (0, 0, 0), -1)
        cv2.putText(output, label, label_top, cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (255, 255, 255), 2)
        
        return output


class MapClassifier(BaseModule):
    name = 'map_classifier'
    version = '3.0.0'
    description = '多尺度模板匹配地图分类器'
    priority = 90
    dependencies = []
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        self._maps_dir = self.get_config('maps_dir')
        if self._maps_dir is None:
            self._maps_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'maps')
        
        self._check_interval = self.get_config('check_interval', 2.0)
        self._confidence_threshold = self.get_config('confidence_threshold', 0.5)
        self._use_pyramid = self.get_config('use_pyramid', True)
        
        self._matcher: Optional[FullscreenTemplateMatcher] = None
        self._current_map: Optional[Dict[str, Any]] = None
        self._map_history: List[Dict[str, Any]] = []
        self._classification_count = 0
        
        self._init_matcher()
    
    def _init_matcher(self):
        if os.path.exists(self._maps_dir):
            self._matcher = FullscreenTemplateMatcher(self._maps_dir)
            self._log(f"加载了 {len(self._matcher.templates)} 个地图模板")
        else:
            self._log(f"地图目录不存在: {self._maps_dir}", level='WARNING')
    
    def _on_start(self):
        self._log('多尺度模板匹配地图分类器已启动')
    
    def _on_stop(self):
        self._log('地图分类器已停止')
    
    def _on_tick(self):
        try:
            from ...core.platform import PlatformManager
            platform = PlatformManager()
            
            screenshot = platform.capture_screen()
            if screenshot is None:
                time.sleep(self._check_interval)
                return
            
            result = self._classify(screenshot)
            
            if result and result['confidence'] >= self._confidence_threshold:
                old_map = self._current_map['map'] if self._current_map else None
                self._current_map = result
                
                self._map_history.append({
                    'timestamp': time.time(),
                    'map': result['map'],
                    'confidence': result['confidence']
                })
                
                if len(self._map_history) > 100:
                    self._map_history.pop(0)
                
                self._classification_count += 1
                
                if old_map != result['map']:
                    from ...core.events import EventBus, EventType
                    event_bus = EventBus()
                    event_bus.publish(
                        'map.changed',
                        event_type=EventType.GAME,
                        data=result,
                        source='map_classifier'
                    )
                    self._log(f"地图切换: {old_map} -> {result['map']}")
            
            time.sleep(self._check_interval)
            
        except Exception as e:
            self._log(f'分类错误: {e}', level='ERROR')
            time.sleep(1)
    
    def _get_search_region(self, screenshot: np.ndarray) -> Tuple[int, int, int, int]:
        h, w = screenshot.shape[:2]
        
        search_width = int(w * 0.35)
        search_height = int(h * 0.4)
        
        x1 = w - search_width
        y1 = 0
        x2 = w
        y2 = search_height
        
        return (x1, y1, x2, y2)
    
    def _classify(self, screenshot: np.ndarray) -> Optional[Dict[str, Any]]:
        if screenshot is None or self._matcher is None:
            return None
        
        try:
            search_region = self._get_search_region(screenshot)
            
            result = self._matcher.match(
                screenshot,
                threshold=self._confidence_threshold,
                use_pyramid=self._use_pyramid,
                search_region=search_region
            )
            
            if result is None:
                return None
            
            all_results = self._matcher.match_all(
                screenshot,
                threshold=0.3,
                use_pyramid=self._use_pyramid,
                search_region=search_region
            )
            
            all_scores = {r.map_name: round(r.confidence, 3) for r in all_results}
            
            return {
                'map': result.map_name,
                'confidence': result.confidence,
                'scale': result.scale,
                'top_left': result.top_left,
                'bottom_right': result.bottom_right,
                'center': self._matcher.get_center(result),
                'size': self._matcher.get_width_height(result),
                'all_scores': all_scores
            }
        except Exception as e:
            self._log(f'分类错误: {e}', level='ERROR')
            return None
    
    def _log(self, message: str, level: str = 'INFO'):
        try:
            from ...core.logger import Logger
            logger = Logger()
            log_method = getattr(logger, level.lower(), logger.info)
            log_method(message, module='MapClassifier')
        except ImportError:
            print(f'[{level}] MapClassifier: {message}')
    
    def get_current_map(self) -> Optional[str]:
        return self._current_map['map'] if self._current_map else None
    
    def get_map_info(self) -> Optional[Dict[str, Any]]:
        return self._current_map
    
    def classify(self, screenshot: np.ndarray) -> Optional[Dict[str, Any]]:
        return self._classify(screenshot)
    
    def get_matcher(self) -> Optional[FullscreenTemplateMatcher]:
        return self._matcher
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'current_map': self._current_map,
            'classification_count': self._classification_count,
            'map_history': self._map_history[-10:],
            'templates_loaded': len(self._matcher.templates) if self._matcher else 0
        }
