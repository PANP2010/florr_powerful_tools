"""
Stats Collector - 数据收集器
收集和分析游戏数据
"""

import os
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from collections import defaultdict
from pathlib import Path

from ..base import BaseModule, ModuleState


class StatsCollector(BaseModule):
    name = 'stats_collector'
    version = '1.0.0'
    description = '数据统计收集器'
    priority = 50
    dependencies = []
    
    PETAL_RARITIES = [
        'common', 'unusual', 'rare', 'epic', 
        'legendary', 'mythic', 'ultra', 'super', 'unique'
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        self._track_petals = self.get_config('track_petals', True)
        self._track_efficiency = self.get_config('track_efficiency', True)
        self._export_format = self.get_config('export_format', 'json')
        self._check_interval = self.get_config('check_interval', 5.0)
        
        self._game_stats = {
            'session_start': None,
            'total_runtime': 0,
            'petals_collected': defaultdict(int),
            'mobs_killed': defaultdict(int),
            'deaths': 0,
            'maps_visited': defaultdict(int),
            'afk_responses': 0,
            'distance_traveled': 0,
        }
        
        self._session_stats = {
            'petals': defaultdict(int),
            'kills': 0,
            'efficiency': 0,
        }
        
        self._history: List[Dict[str, Any]] = []
        self._last_position = None
        self._stats_file = None
    
    def _on_start(self):
        self._game_stats['session_start'] = time.time()
        self._setup_stats_file()
        self._subscribe_events()
        self._log('数据收集器已启动')
    
    def _on_stop(self):
        self._save_session_stats()
        self._log('数据收集器已停止')
    
    def _on_tick(self):
        try:
            self._update_efficiency()
            
            if len(self._history) % 10 == 0:
                self._save_session_stats()
            
            time.sleep(self._check_interval)
            
        except Exception as e:
            self._log(f'统计错误: {e}', level='ERROR')
            time.sleep(1)
    
    def _setup_stats_file(self):
        root_path = Path(__file__).parent.parent.parent
        stats_dir = root_path / 'logs' / 'stats'
        stats_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self._stats_file = stats_dir / f'stats_{timestamp}.json'
    
    def _subscribe_events(self):
        from ...core.events import EventBus
        event_bus = EventBus()
        
        event_bus.subscribe('mob.attacked', self._on_mob_attacked)
        event_bus.subscribe('afk.detected', self._on_afk_detected)
        event_bus.subscribe('map.changed', self._on_map_changed)
    
    def _on_mob_attacked(self, event):
        mob_class = event.data.get('target', {}).get('class', 'unknown')
        self._game_stats['mobs_killed'][mob_class] += 1
        self._session_stats['kills'] += 1
        
        self._record_event('kill', {'mob': mob_class})
    
    def _on_afk_detected(self, event):
        self._game_stats['afk_responses'] += 1
        self._record_event('afk_response', {})
    
    def _on_map_changed(self, event):
        map_name = event.data.get('map', 'unknown')
        self._game_stats['maps_visited'][map_name] += 1
        self._record_event('map_change', {'map': map_name})
    
    def record_petal_drop(self, petal_name: str, rarity: str):
        if not self._track_petals:
            return
        
        self._game_stats['petals_collected'][petal_name] += 1
        self._session_stats['petals'][petal_name] += 1
        
        self._record_event('petal_drop', {
            'petal': petal_name,
            'rarity': rarity
        })
        
        from ...core.events import EventBus, EventType
        event_bus = EventBus()
        event_bus.publish(
            'petal.collected',
            event_type=EventType.GAME,
            data={'petal': petal_name, 'rarity': rarity},
            source='stats_collector'
        )
    
    def record_death(self):
        self._game_stats['deaths'] += 1
        self._record_event('death', {})
    
    def update_position(self, x: float, y: float):
        if self._last_position:
            dx = x - self._last_position[0]
            dy = y - self._last_position[1]
            distance = (dx ** 2 + dy ** 2) ** 0.5
            self._game_stats['distance_traveled'] += distance
        
        self._last_position = (x, y)
    
    def _update_efficiency(self):
        if not self._track_efficiency:
            return
        
        session_time = time.time() - self._game_stats['session_start']
        if session_time > 0:
            total_petals = sum(self._session_stats['petals'].values())
            self._session_stats['efficiency'] = total_petals / (session_time / 3600)
    
    def _record_event(self, event_type: str, data: Dict[str, Any]):
        self._history.append({
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'type': event_type,
            'data': data
        })
        
        if len(self._history) > 10000:
            self._history = self._history[-5000:]
    
    def _save_session_stats(self):
        if not self._stats_file:
            return
        
        try:
            stats_data = {
                'session': {
                    'start': datetime.fromtimestamp(self._game_stats['session_start']).isoformat() if self._game_stats['session_start'] else None,
                    'runtime': time.time() - self._game_stats['session_start'] if self._game_stats['session_start'] else 0,
                },
                'totals': {
                    'petals': dict(self._game_stats['petals_collected']),
                    'kills': dict(self._game_stats['mobs_killed']),
                    'deaths': self._game_stats['deaths'],
                    'afk_responses': self._game_stats['afk_responses'],
                    'distance': self._game_stats['distance_traveled'],
                },
                'maps': dict(self._game_stats['maps_visited']),
                'session_stats': {
                    'petals': dict(self._session_stats['petals']),
                    'kills': self._session_stats['kills'],
                    'efficiency': round(self._session_stats['efficiency'], 2),
                },
                'history': self._history[-100:],
            }
            
            with open(self._stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self._log(f'保存统计失败: {e}', level='ERROR')
    
    def export_report(self, format: str = None) -> str:
        fmt = format or self._export_format
        
        if fmt == 'json':
            return self._export_json()
        elif fmt == 'csv':
            return self._export_csv()
        else:
            return self._export_text()
    
    def _export_json(self) -> str:
        return json.dumps({
            'stats': dict(self._game_stats),
            'session': dict(self._session_stats),
        }, indent=2, default=str)
    
    def _export_csv(self) -> str:
        lines = ['category,item,count']
        
        for petal, count in self._game_stats['petals_collected'].items():
            lines.append(f'petal,{petal},{count}')
        
        for mob, count in self._game_stats['mobs_killed'].items():
            lines.append(f'mob,{mob},{count}')
        
        return '\n'.join(lines)
    
    def _export_text(self) -> str:
        lines = [
            '=== Florr Assistant 统计报告 ===',
            f'会话时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            '',
            '--- 花瓣收集 ---',
        ]
        
        for petal, count in sorted(self._game_stats['petals_collected'].items()):
            lines.append(f'  {petal}: {count}')
        
        lines.extend([
            '',
            '--- 击杀统计 ---',
        ])
        
        for mob, count in sorted(self._game_stats['mobs_killed'].items()):
            lines.append(f'  {mob}: {count}')
        
        lines.extend([
            '',
            '--- 其他 ---',
            f'  死亡次数: {self._game_stats["deaths"]}',
            f'  AFK响应: {self._game_stats["afk_responses"]}',
            f'  效率: {self._session_stats["efficiency"]:.2f} 花瓣/小时',
        ])
        
        return '\n'.join(lines)
    
    def _log(self, message: str, level: str = 'INFO'):
        from ...core.logger import Logger
        logger = Logger()
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message, module='StatsCollector')
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'totals': {
                'petals': sum(self._game_stats['petals_collected'].values()),
                'kills': sum(self._game_stats['mobs_killed'].values()),
                'deaths': self._game_stats['deaths'],
            },
            'session': {
                'petals': sum(self._session_stats['petals'].values()),
                'kills': self._session_stats['kills'],
                'efficiency': round(self._session_stats['efficiency'], 2),
            },
            'runtime': time.time() - self._game_stats['session_start'] if self._game_stats['session_start'] else 0,
        }
    
    def get_petal_stats(self) -> Dict[str, int]:
        return dict(self._game_stats['petals_collected'])
    
    def get_kill_stats(self) -> Dict[str, int]:
        return dict(self._game_stats['mobs_killed'])
