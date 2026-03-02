"""
Data Collector - 数据收集模块
收集游戏操作数据用于训练AI模型
"""

import os
import time
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from collections import deque
from dataclasses import dataclass, asdict
import numpy as np
import cv2

from ..base import BaseModule, ModuleState


@dataclass
class GameState:
    health_percent: float
    health_florr: int
    degree: float
    yinyang: int
    mobs: List[List[float]]
    timestamp: float


@dataclass
class PlayerAction:
    move_x: float
    move_y: float
    attack: bool
    defend: bool
    yinyang_toggle: bool
    timestamp: float


@dataclass
class TrainingSample:
    state: Dict[str, Any]
    action: Dict[str, Any]
    timestamp: float
    map_name: str = "unknown"


class DataCollector(BaseModule):
    name = 'data_collector'
    version = '1.0.0'
    description = '训练数据收集器'
    priority = 95
    dependencies = []
    
    MAX_MOBS = 10
    SAMPLE_INTERVAL = 0.1
    
    MOB_TYPES = [
        "ant_baby", "ant_egg", "ant_hole", "ant_queen", "ant_soldier", "ant_worker",
        "assembler", "barrel", "bee", "beetle", "beetle_hel", "beetle_mummy", 
        "beetle_nazar", "beetle_pharaoh", "bubble", "bumble_bee", "bush",
        "cactus", "centipede", "centipede_body", "centipede_desert", 
        "centipede_desert_body", "centipede_evil", "centipede_evil_body",
        "centipede_hel", "centipede_hel_body", "crab", "crab_mecha",
        "dandelion", "digger", "dummy", "fire_ant_baby", "fire_ant_burrow",
        "fire_ant_egg", "fire_ant_queen", "fire_ant_soldier", "fire_ant_worker",
        "firefly", "firefly_magic", "fly", "gambler", "gambler_old", "hornet",
        "jellyfish", "ladybug", "ladybug_dark", "ladybug_shiny", "leafbug",
        "leafbug_shiny", "leech", "leech_body", "mantis", "mecha_flower",
        "mecha_flower_old", "moth", "oracle", "roach", "rock", "sandstorm",
        "scorpion", "shell", "spider", "spider_hel", "spider_mecha", "sponge",
        "square", "starfish", "termite_baby", "termite_egg", "termite_mound",
        "termite_overmind", "termite_soldier", "termite_worker", "titan",
        "tomb", "trader", "wasp", "wasp_hel", "wasp_mecha", "worm", "worm_guts"
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        self._output_dir = self.get_config('output_dir', 'data/training')
        self._sample_interval = self.get_config('sample_interval', 0.1)
        self._auto_save = self.get_config('auto_save', True)
        self._save_interval = self.get_config('save_interval', 60)
        
        self._mob_model = None
        self._current_map = "unknown"
        
        self._samples: deque = deque(maxlen=100000)
        self._sample_count = 0
        self._session_start = None
        self._last_save_time = 0
        
        self._mouse_pos = (0, 0)
        self._mouse_pressed = {'left': False, 'right': False, 'middle': False}
        self._keys_pressed = set()
        
        self._callbacks: List[Callable] = []
        self._collecting = False
        
        self._screen_center = (960, 540)
        self._last_yinyang = 0
    
    def _on_start(self):
        self._load_mob_model()
        self._setup_output_dir()
        self._start_input_listeners()
        self._log('数据收集器已启动')
    
    def _on_stop(self):
        self._save_session()
        self._stop_input_listeners()
        self._log(f'数据收集器已停止，共收集 {self._sample_count} 条数据')
    
    def _on_tick(self):
        if not self._collecting:
            time.sleep(0.5)
            return
        
        try:
            sample = self._collect_sample()
            if sample:
                self._samples.append(sample)
                self._sample_count += 1
                
                for callback in self._callbacks:
                    try:
                        callback(sample)
                    except:
                        pass
                
                if self._auto_save and time.time() - self._last_save_time > self._save_interval:
                    self._save_session()
                    self._last_save_time = time.time()
            
            time.sleep(self._sample_interval)
            
        except Exception as e:
            self._log(f'收集错误: {e}', level='ERROR')
            time.sleep(0.5)
    
    def _load_mob_model(self):
        try:
            from ultralytics import YOLO
            
            model_path = self._resolve_model_path()
            self._log(f'尝试加载模型: {model_path}')
            
            if os.path.exists(model_path):
                self._mob_model = YOLO(model_path)
                self._log(f'怪物检测模型加载成功: {model_path}')
            else:
                self._log(f'模型文件不存在: {model_path}', level='WARNING')
                all_paths = self._get_all_model_paths()
                self._log(f'已搜索路径: {all_paths}', level='DEBUG')
        except ImportError as e:
            self._log(f'ultralytics未安装: {e}', level='WARNING')
        except Exception as e:
            self._log(f'模型加载失败: {e}', level='ERROR')
            import traceback
            traceback.print_exc()
    
    def _get_all_model_paths(self) -> list:
        root = Path(__file__).parent.parent.parent
        return [
            str(root / 'models' / 'mob_detector.pt'),
            str(root / 'models' / 'stf_det_all.pt'),
            str(root.parent / 'florr-auto-framework-pytorch' / 'models' / 'new_mob_dataset' / 'stf_det_all.pt'),
            str(root.parent / 'florr-auto-framework-pytorch-macos' / 'models' / 'new_mob_dataset' / 'stf_det_all.pt'),
            str(root.parent / 'florr-auto-framework-pytorch' / 'mob_detector' / 'weights' / 'best.pt'),
            str(root.parent / 'florr-auto-framework-pytorch-macos' / 'mob_detector' / 'weights' / 'best.pt'),
        ]
    
    def _resolve_model_path(self) -> str:
        root = Path(__file__).parent.parent.parent
        
        paths = [
            root / 'models' / 'mob_detector.pt',
            root / 'models' / 'stf_det_all.pt',
            root.parent / 'florr-auto-framework-pytorch' / 'models' / 'new_mob_dataset' / 'stf_det_all.pt',
            root.parent / 'florr-auto-framework-pytorch-macos' / 'models' / 'new_mob_dataset' / 'stf_det_all.pt',
            root.parent / 'florr-auto-framework-pytorch' / 'mob_detector' / 'weights' / 'best.pt',
            root.parent / 'florr-auto-framework-pytorch-macos' / 'mob_detector' / 'weights' / 'best.pt',
        ]
        
        for p in paths:
            if p.exists():
                return str(p)
        
        return str(paths[0])
    
    def _setup_output_dir(self):
        output_path = Path(self._output_dir)
        if not output_path.is_absolute():
            root = Path(__file__).parent.parent.parent
            output_path = root / self._output_dir
        output_path.mkdir(parents=True, exist_ok=True)
        self._output_path = output_path
    
    def _start_input_listeners(self):
        try:
            from pynput import mouse, keyboard
            
            self._mouse_listener = mouse.Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click
            )
            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self._mouse_listener.start()
            self._keyboard_listener.start()
        except ImportError:
            self._log('pynput未安装，输入监听不可用', level='WARNING')
    
    def _stop_input_listeners(self):
        if hasattr(self, '_mouse_listener'):
            self._mouse_listener.stop()
        if hasattr(self, '_keyboard_listener'):
            self._keyboard_listener.stop()
    
    def _on_mouse_move(self, x, y):
        self._mouse_pos = (x, y)
    
    def _on_mouse_click(self, x, y, button, pressed):
        button_name = str(button).replace('Button.', '')
        self._mouse_pressed[button_name] = pressed
    
    def _on_key_press(self, key):
        try:
            key_name = key.char if hasattr(key, 'char') and key.char else str(key)
            self._keys_pressed.add(key_name)
        except:
            pass
    
    def _on_key_release(self, key):
        try:
            key_name = key.char if hasattr(key, 'char') and key.char else str(key)
            self._keys_pressed.discard(key_name)
        except:
            pass
    
    def _collect_sample(self) -> Optional[TrainingSample]:
        try:
            from ...core.platform import PlatformManager
            platform = PlatformManager()
            
            screenshot = platform.capture_screen()
            if screenshot is None:
                return None
            
            state = self._extract_state(screenshot)
            action = self._extract_action()
            
            if state and action:
                return TrainingSample(
                    state=state,
                    action=action,
                    timestamp=time.time(),
                    map_name=self._current_map
                )
        except Exception as e:
            self._log(f'样本收集错误: {e}', level='DEBUG')
        
        return None
    
    def _extract_state(self, screenshot: np.ndarray) -> Optional[Dict[str, Any]]:
        health = self._detect_health(screenshot)
        mobs = self._detect_mobs(screenshot)
        degree = self._detect_degree(screenshot)
        yinyang = self._detect_yinyang(screenshot)
        
        return {
            'health_percent': health['percent'],
            'health_florr': health['florr'],
            'degree': degree,
            'yinyang': yinyang,
            'mobs': mobs[:self.MAX_MOBS] if mobs else [],
            'mob_count': len(mobs) if mobs else 0
        }
    
    def _detect_health(self, image: np.ndarray) -> Dict[str, Any]:
        try:
            h, w = image.shape[:2]
            
            health_bar_region = image[90:110, 100:280]
            
            if health_bar_region.size == 0:
                return {'percent': 100, 'florr': 32041}
            
            hsv = cv2.cvtColor(health_bar_region, cv2.COLOR_BGR2HSV)
            lower_green = np.array([35, 50, 50])
            upper_green = np.array([85, 255, 255])
            mask = cv2.inRange(hsv, lower_green, upper_green)
            
            green_pixels = cv2.countNonZero(mask)
            total_pixels = mask.shape[0] * mask.shape[1]
            
            percent = (green_pixels / total_pixels) * 100 if total_pixels > 0 else 0
            florr = int(percent * 349.54)
            
            return {'percent': round(percent, 2), 'florr': florr}
        except:
            return {'percent': 100, 'florr': 32041}
    
    def _detect_mobs(self, image: np.ndarray) -> List[List[float]]:
        mobs = []
        
        if self._mob_model is not None:
            try:
                results = self._mob_model(image, verbose=False)
                
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        h, w = image.shape[:2]
                        
                        for box in boxes:
                            confidence = float(box.conf[0])
                            if confidence >= 0.5:
                                x1, y1, x2, y2 = box.xyxy[0].tolist()
                                class_id = int(box.cls[0])
                                class_name = result.names.get(class_id, 'unknown')
                                
                                center_x = (x1 + x2) / 2 / w
                                center_y = (y1 + y2) / 2 / h
                                width = (x2 - x1) / w
                                height = (y2 - y1) / h
                                
                                mob_one_hot = self._one_hot_mob(class_name)
                                
                                mobs.append([
                                    center_x, center_y, width, height,
                                    *mob_one_hot
                                ])
            except Exception as e:
                self._log(f'怪物检测错误: {e}', level='DEBUG')
        
        return mobs
    
    def _one_hot_mob(self, mob_name: str) -> List[int]:
        try:
            idx = self.MOB_TYPES.index(mob_name)
            return [1 if i == idx else 0 for i in range(len(self.MOB_TYPES))]
        except ValueError:
            return [0] * len(self.MOB_TYPES)
    
    def _detect_degree(self, image: np.ndarray) -> float:
        return 0.5
    
    def _detect_yinyang(self, image: np.ndarray) -> int:
        return self._last_yinyang
    
    def _extract_action(self) -> Dict[str, Any]:
        mx, my = self._mouse_pos
        cx, cy = self._screen_center
        
        dx = mx - cx
        dy = my - cy
        
        max_dist = max(abs(dx), abs(dy), 1)
        move_x = dx / max_dist
        move_y = dy / max_dist
        
        attack = self._mouse_pressed.get('left', False)
        defend = self._mouse_pressed.get('right', False)
        yinyang_toggle = 'e' in self._keys_pressed or 'E' in self._keys_pressed
        
        if yinyang_toggle:
            self._last_yinyang = 1 - self._last_yinyang
        
        return {
            'move_x': round(move_x, 4),
            'move_y': round(move_y, 4),
            'attack': 1.0 if attack else 0.0,
            'defend': 1.0 if defend else 0.0,
            'yinyang': 1.0 if yinyang_toggle else 0.0
        }
    
    def start_collecting(self):
        self._collecting = True
        self._session_start = time.time()
        self._log('开始收集数据...')
    
    def stop_collecting(self):
        self._collecting = False
        self._save_session()
        self._log(f'停止收集，共 {self._sample_count} 条数据')
    
    def toggle_collecting(self) -> bool:
        if self._collecting:
            self.stop_collecting()
        else:
            self.start_collecting()
        return self._collecting
    
    def set_map(self, map_name: str):
        self._current_map = map_name
        self._log(f'当前地图: {map_name}')
    
    def _save_session(self):
        if not self._samples:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data_{self._current_map}_{timestamp}.jsonl'
        filepath = self._output_path / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for sample in self._samples:
                    data = {
                        'state': sample.state,
                        'action': sample.action,
                        'timestamp': sample.timestamp,
                        'map': sample.map_name
                    }
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')
            
            self._log(f'数据已保存: {filepath} ({len(self._samples)} 条)')
            self._samples.clear()
            
        except Exception as e:
            self._log(f'保存失败: {e}', level='ERROR')
    
    def add_callback(self, callback: Callable):
        self._callbacks.append(callback)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'collecting': self._collecting,
            'sample_count': self._sample_count,
            'session_samples': len(self._samples),
            'current_map': self._current_map,
            'session_duration': time.time() - self._session_start if self._session_start else 0
        }
    
    def _log(self, message: str, level: str = 'INFO'):
        from ...core.logger import Logger
        logger = Logger()
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message, module='DataCollector')
