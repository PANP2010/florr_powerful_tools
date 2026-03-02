"""
数据质量分析脚本
分析训练数据的质量并生成报告
"""

import json
import statistics
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict


class DataQualityReport:
    def __init__(self, file_path: str):
        self.file = file_path
        self.total_samples = 0
        self.valid_samples = 0
        self.issues = defaultdict(int)
        self.stats = {
            'health': [],
            'mob_count': [],
            'attack_rate': [],
            'defend_rate': [],
            'move_x': [],
            'move_y': []
        }
        self.mob_types = defaultdict(int)
        self.maps = defaultdict(int)
    
    def add_sample(self, sample: Dict[str, Any]):
        self.total_samples += 1
        
        state = sample.get('state', {})
        action = sample.get('action', {})
        
        has_valid_state = False
        has_valid_action = False
        
        if state:
            health = state.get('health', state.get('health_percent', 0))
            if isinstance(health, (int, float)):
                self.stats['health'].append(health)
            
            mobs = state.get('mobs', [])
            if isinstance(mobs, list):
                self.stats['mob_count'].append(len(mobs))
                
                for mob in mobs:
                    if isinstance(mob, list) and len(mob) >= 7:
                        if mob[4] == 1:
                            self.mob_types['starfish'] += 1
                        elif mob[5] == 1:
                            self.mob_types['jellyfish'] += 1
                        elif mob[6] == 1:
                            self.mob_types['bubble'] += 1
            
            has_valid_state = True
        
        map_name = sample.get('map', 'unknown')
        self.maps[map_name] += 1
        
        if action:
            attack = action.get('attack', 0)
            defend = action.get('defend', 0)
            
            if isinstance(attack, (int, float)):
                self.stats['attack_rate'].append(attack)
            if isinstance(defend, (int, float)):
                self.stats['defend_rate'].append(defend)
            
            move_x = action.get('move_x', 0)
            move_y = action.get('move_y', 0)
            if isinstance(move_x, (int, float)):
                self.stats['move_x'].append(move_x)
            if isinstance(move_y, (int, float)):
                self.stats['move_y'].append(move_y)
            
            has_valid_action = True
        
        if has_valid_state and has_valid_action:
            self.valid_samples += 1
        else:
            self.issues['invalid_format'] += 1
        
        if state and 'mobs' in state:
            mobs = state['mobs']
            if not isinstance(mobs, list):
                self.issues['invalid_mobs_format'] += 1
            elif len(mobs) == 0:
                self.issues['empty_mobs'] += 1
        
        if state and ('health' in state or 'health_percent' in state):
            health = state.get('health', state.get('health_percent', 0))
            if health <= 0:
                self.issues['zero_health'] += 1
        
        if action and 'attack' in action and 'defend' in action:
            if action['attack'] == 0 and action['defend'] == 0:
                self.issues['no_action'] += 1


class DataQualityAnalyzer:
    def __init__(self):
        self.reports = []
    
    def analyze_directory(self, dir_path: Path) -> DataQualityReport:
        report = DataQualityReport(file_path=str(dir_path))
        
        jsonl_files = list(dir_path.glob('*.jsonl'))
        
        if not jsonl_files:
            print(f"未找到数据文件: {dir_path}")
            return report
        
        print(f"分析目录: {dir_path}")
        print(f"找到 {len(jsonl_files)} 个数据文件")
        
        for file_path in jsonl_files:
            self.analyze_file(file_path, report)
        
        return report
    
    def analyze_file(self, file_path: Path, report: DataQualityReport):
        print(f"  分析文件: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        sample = json.loads(line)
                        report.add_sample(sample)
                    except json.JSONDecodeError:
                        report.issues['json_parse_error'] += 1
        except Exception as e:
            print(f"  错误: {e}")
        
        return report


def print_report(results: Dict[str, Any]):
    print(f"\n{'='*60}")
    print(f"数据质量报告: {results['file']}")
    print(f"{'='*60}")
    
    print(f"\n📊 基本统计:")
    print(f"  总样本数: {results['total_samples']}")
    if results['total_samples'] > 0:
        print(f"  有效样本数: {results['valid_samples']} ({results['valid_samples']/results['total_samples']*100:.1f}%)")
    else:
        print(f"  有效样本数: {results['valid_samples']}")
    
    if results['issues']:
        print(f"\n⚠️ 问题统计:")
        for issue, count in sorted(results['issues'].items(), key=lambda x: -x[1]):
            pct = count / max(results['total_samples'], 1) * 100
            print(f"  {issue}: {count} ({pct:.1f}%)")
    
    print(f"\n📈 数值分布:")
    for stat_name, values in results['stats'].items():
        if values:
            print(f"  {stat_name}:")
            print(f"    min={min(values):.4f}, max={max(values):.4f}, mean={statistics.mean(values):.4f}, median={statistics.median(values):.4f}")
    
    if results['mob_types']:
        print(f"\n👾 怪物类型分布:")
        total_mobs = sum(results['mob_types'].values())
        if total_mobs > 0:
            for mob_type, count in sorted(results['mob_types'].items(), key=lambda x: -x[1]):
                pct = count / total_mobs * 100
                print(f"  {mob_type}: {count} ({pct:.1f}%)")
    
    if results['maps']:
        print(f"\n🗺️ 地图分布:")
        for map_name, count in sorted(results['maps'].items(), key=lambda x: -x[1]):
            pct = count / max(results['total_samples'], 1) * 100
            print(f"  {map_name}: {count} ({pct:.1f}%)")
    
    if results['total_samples'] > 0:
        quality_score = results['valid_samples'] / results['total_samples'] * 100
        print(f"\n✅ 数据质量评分: {quality_score:.1f}/100")
        
        if quality_score < 30:
            print("  ❌ 数据质量极差，建议重新收集")
        elif quality_score < 60:
            print("  ⚠️ 数据质量较差，需要清洗或补充收集")
        elif quality_score < 80:
            print("  👍 数据质量良好")
        else:
            print("  🌟 数据质量优秀")


def main():
    data_dirs = [
        Path('/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/florr-auto-framework-pytorch/trains/data'),
        Path('/Users/panjiyang/Documents/trae_projects/florr_powerful_tools/florr_assistant/data/training'),
    ]
    
    analyzer = DataQualityAnalyzer()
    
    all_reports = []
    
    for dir_path in data_dirs:
        if dir_path.exists():
            report = analyzer.analyze_directory(dir_path)
            all_reports.append(report)
            print_report({
                'file': report.file,
                'total_samples': report.total_samples,
                'valid_samples': report.valid_samples,
                'issues': dict(report.issues),
                'stats': report.stats,
                'mob_types': dict(report.mob_types),
                'maps': dict(report.maps)
            })
    
    if not all_reports:
        print("未找到任何数据文件")
        return
    
    print(f"\n{'='*60}")
    print("汇总报告")
    print(f"{'='*60}")
    
    total_samples = sum(r.total_samples for r in all_reports)
    total_valid = sum(r.valid_samples for r in all_reports)
    
    print(f"\n总样本数: {total_samples}")
    print(f"有效样本数: {total_valid}")
    if total_samples > 0:
        print(f"整体质量评分: {total_valid/total_samples*100:.1f}/100")


if __name__ == '__main__':
    main()
