"""
AFK Responder - AFK响应器
自动响应游戏中的AFK验证
"""

import os
import time
import random
from typing import Optional, Dict, Any, List, Tuple
import numpy as np

from ..base import BaseModule, ModuleState


class AFKResponder(BaseModule):
    name = 'afk_responder'
    version = '1.0.0'
    description = 'AFK验证响应器'
    priority = 99
    dependencies = ['afk_detector']
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        self._auto_respond = self.get_config('auto_respond', True)
        self._llm_enabled = self.get_config('llm_enabled', False)
        self._llm_provider = self.get_config('llm_provider', 'ollama')
        self._llm_model = self.get_config('llm_model', 'qwen2.5:14b')
        
        self._response_count = 0
        self._last_response = None
        self._cooldown = 2.0
        self._last_action_time = 0
    
    def _on_start(self):
        self._subscribe_events()
        self._log('AFK响应器已启动')
    
    def _on_stop(self):
        self._log('AFK响应器已停止')
    
    def _on_tick(self):
        time.sleep(0.5)
    
    def _subscribe_events(self):
        from ...core.events import EventBus, EventType
        event_bus = EventBus()
        event_bus.subscribe('afk.detected', self._on_afk_detected)
    
    def _on_afk_detected(self, event):
        if not self._auto_respond:
            return
        
        current_time = time.time()
        if current_time - self._last_action_time < self._cooldown:
            return
        
        detections = event.data.get('detections', [])
        if not detections:
            return
        
        self._log(f'检测到AFK窗口，准备响应...')
        
        try:
            self._respond(detections)
            self._last_action_time = current_time
            self._response_count += 1
            self._last_response = {
                'timestamp': current_time,
                'detections': detections
            }
        except Exception as e:
            self._log(f'响应失败: {e}', level='ERROR')
    
    def _respond(self, detections: List[Dict[str, Any]]):
        from ...core.platform import PlatformManager
        platform = PlatformManager()
        
        for detection in detections:
            bbox = detection.get('bbox', [])
            class_name = detection.get('class', '')
            
            if len(bbox) >= 4:
                x, y, w, h = bbox
                center_x = x + w // 2
                center_y = y + h // 2
                
                if 'button' in class_name.lower() or 'click' in class_name.lower():
                    self._click_button(center_x, center_y)
                elif 'dialog' in class_name.lower() or 'chat' in class_name.lower():
                    self._handle_dialog(center_x, center_y, bbox)
                else:
                    self._click_button(center_x, center_y)
    
    def _click_button(self, x: int, y: int):
        from ...core.platform import PlatformManager
        platform = PlatformManager()
        
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        
        platform.mouse_move(x + offset_x, y + offset_y, smooth=True)
        time.sleep(random.uniform(0.1, 0.3))
        platform.mouse_click(x + offset_x, y + offset_y)
        
        self._log(f'点击位置: ({x + offset_x}, {y + offset_y})')
    
    def _handle_dialog(self, x: int, y: int, bbox: List[int]):
        self._log('检测到对话框，尝试处理...')
        
        if self._llm_enabled:
            response = self._get_llm_response()
            if response:
                self._type_response(response)
        else:
            self._click_button(x + 50, y + bbox[3] - 20)
    
    def _get_llm_response(self) -> Optional[str]:
        try:
            if self._llm_provider == 'ollama':
                return self._query_ollama()
            elif self._llm_provider == 'openai':
                return self._query_openai()
        except Exception as e:
            self._log(f'LLM查询失败: {e}', level='ERROR')
        
        return None
    
    def _query_ollama(self) -> Optional[str]:
        try:
            import requests
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self._llm_model,
                    'prompt': 'Respond briefly to verify you are active in a game. Just say something short and friendly.',
                    'stream': False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')[:50]
        except Exception as e:
            self._log(f'Ollama请求失败: {e}', level='WARNING')
        
        return None
    
    def _query_openai(self) -> Optional[str]:
        try:
            import openai
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=self._llm_model,
                messages=[{
                    'role': 'user',
                    'content': 'Say something short and friendly to verify activity.'
                }],
                max_tokens=20
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self._log(f'OpenAI请求失败: {e}', level='WARNING')
        
        return None
    
    def _type_response(self, text: str):
        from ...core.platform import PlatformManager
        platform = PlatformManager()
        
        platform.key_click(x=None, y=None)
        time.sleep(0.2)
        platform.key_type(text, interval=0.05)
        time.sleep(0.2)
        platform.key_press('enter')
        
        self._log(f'输入响应: {text}')
    
    def _log(self, message: str, level: str = 'INFO'):
        from ...core.logger import Logger
        logger = Logger()
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message, module='AFKResponder')
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'response_count': self._response_count,
            'last_response': self._last_response,
            'auto_respond': self._auto_respond,
            'llm_enabled': self._llm_enabled
        }
