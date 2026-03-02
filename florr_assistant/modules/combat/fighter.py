"""
Fighter - 自动战斗器
自动攻击怪物和规避危险
"""

import os
import time
import math
import random
from typing import Optional, Dict, Any, List, Tuple
import numpy as np

from ..base import BaseModule, ModuleState


class Fighter(BaseModule):
    name = 'fighter'
    version = '1.0.0'
    description = '自动战斗器'
    priority = 75
    dependencies = ['target_selector']
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        self._auto_dodge = self.get_config('auto_dodge', True)
        self._sandstorm_avoid = self.get_config('sandstorm_avoid', True)
        self._check_interval = self.get_config('check_interval', 0.15)
        self._attack_range = self.get_config('attack_range', 200)
        
        self._kill_count = 0
        self._dodge_count = 0
        self._last_attack_time = 0
        self._attack_cooldown = 0.1
        self._current_target: Optional[Dict[str, Any]] = None
        self._is_dodging = False
    
    def _on_start(self):
        self._subscribe_events()
        self._log('战斗器已启动')
    
    def _on_stop(self):
        self._log('战斗器已停止')
    
    def _on_tick(self):
        try:
            if self._current_target:
                if self._should_dodge():
                    self._dodge()
                else:
                    self._attack()
            
            time.sleep(self._check_interval)
            
        except Exception as e:
            self._log(f'战斗错误: {e}', level='ERROR')
            time.sleep(0.5)
    
    def _subscribe_events(self):
        from ...core.events import EventBus
        event_bus = EventBus()
        event_bus.subscribe('mobs.detected', self._on_mobs_detected)
    
    def _on_mobs_detected(self, event):
        self._current_target = event.data.get('selected')
    
    def _should_dodge(self) -> bool:
        if not self._auto_dodge or not self._current_target:
            return False
        
        danger = self._current_target.get('info', {}).get('danger', 0)
        
        if self._sandstorm_avoid and self._current_target.get('class', '').lower() == 'sandstorm':
            return True
        
        return danger > 0.7
    
    def _dodge(self):
        if self._is_dodging:
            return
        
        self._is_dodging = True
        self._dodge_count += 1
        
        from ...core.platform import PlatformManager
        platform = PlatformManager()
        
        directions = ['w', 's', 'a', 'd']
        
        if self._current_target:
            target_center = self._current_target.get('center', (0, 0))
            screen_size = platform.get_screen_size()
            player_pos = (screen_size[0] // 2, screen_size[1] // 2)
            
            dx = player_pos[0] - target_center[0]
            dy = player_pos[1] - target_center[1]
            
            if abs(dx) > abs(dy):
                directions = ['a', 'd'] if dx > 0 else ['d', 'a']
            else:
                directions = ['w', 's'] if dy > 0 else ['s', 'w']
        
        direction = random.choice(directions)
        platform.key_press(direction)
        time.sleep(0.1)
        
        self._log(f'闪避: {direction}')
        
        self._is_dodging = False
    
    def _attack(self):
        current_time = time.time()
        
        if current_time - self._last_attack_time < self._attack_cooldown:
            return
        
        if not self._current_target:
            return
        
        from ...core.platform import PlatformManager
        platform = PlatformManager()
        
        target_center = self._current_target.get('center', (0, 0))
        screen_size = platform.get_screen_size()
        player_pos = (screen_size[0] // 2, screen_size[1] // 2)
        
        distance = math.sqrt(
            (target_center[0] - player_pos[0]) ** 2 +
            (target_center[1] - player_pos[1]) ** 2
        )
        
        if distance > self._attack_range:
            self._move_towards(target_center, player_pos)
        else:
            self._perform_attack(target_center)
        
        self._last_attack_time = current_time
    
    def _move_towards(self, target: Tuple[int, int], player: Tuple[int, int]):
        from ...core.platform import PlatformManager
        platform = PlatformManager()
        
        dx = target[0] - player[0]
        dy = target[1] - player[1]
        
        if abs(dx) > 20:
            platform.key_press('d' if dx > 0 else 'a')
        
        if abs(dy) > 20:
            platform.key_press('s' if dy > 0 else 'w')
    
    def _perform_attack(self, target: Tuple[int, int]):
        from ...core.platform import PlatformManager
        platform = PlatformManager()
        
        platform.mouse_click(target[0], target[1])
        
        self._kill_count += 1
        
        from ...core.events import EventBus, EventType
        event_bus = EventBus()
        event_bus.publish(
            'mob.attacked',
            event_type=EventType.GAME,
            data={'target': target, 'count': self._kill_count},
            source='fighter'
        )
    
    def _log(self, message: str, level: str = 'INFO'):
        from ...core.logger import Logger
        logger = Logger()
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message, module='Fighter')
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'kill_count': self._kill_count,
            'dodge_count': self._dodge_count,
            'current_target': self._current_target,
            'is_dodging': self._is_dodging
        }
