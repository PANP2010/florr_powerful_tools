"""
测试Florr Assistant模块加载
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    print("=" * 50)
    print("测试模块导入...")
    print("=" * 50)
    
    errors = []
    
    try:
        from florr_assistant.core.config import Config
        print("✓ Config 导入成功")
    except Exception as e:
        errors.append(f"Config 导入失败: {e}")
        print(f"✗ Config 导入失败: {e}")
    
    try:
        from florr_assistant.core.logger import Logger
        print("✓ Logger 导入成功")
    except Exception as e:
        errors.append(f"Logger 导入失败: {e}")
        print(f"✗ Logger 导入失败: {e}")
    
    try:
        from florr_assistant.core.events import EventBus
        print("✓ EventBus 导入成功")
    except Exception as e:
        errors.append(f"EventBus 导入失败: {e}")
        print(f"✗ EventBus 导入失败: {e}")
    
    try:
        from florr_assistant.core.platform import PlatformManager
        print("✓ PlatformManager 导入成功")
    except Exception as e:
        errors.append(f"PlatformManager 导入失败: {e}")
        print(f"✗ PlatformManager 导入失败: {e}")
    
    try:
        from florr_assistant.core.engine import Engine
        print("✓ Engine 导入成功")
    except Exception as e:
        errors.append(f"Engine 导入失败: {e}")
        print(f"✗ Engine 导入失败: {e}")
    
    print()
    print("=" * 50)
    print("测试功能模块导入...")
    print("=" * 50)
    
    try:
        from florr_assistant.modules.afk.detector import AFKDetector
        print("✓ AFKDetector 导入成功")
    except Exception as e:
        errors.append(f"AFKDetector 导入失败: {e}")
        print(f"✗ AFKDetector 导入失败: {e}")
    
    try:
        from florr_assistant.modules.afk.responder import AFKResponder
        print("✓ AFKResponder 导入成功")
    except Exception as e:
        errors.append(f"AFKResponder 导入失败: {e}")
        print(f"✗ AFKResponder 导入失败: {e}")
    
    try:
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        print("✓ MapClassifier 导入成功")
    except Exception as e:
        errors.append(f"MapClassifier 导入失败: {e}")
        print(f"✗ MapClassifier 导入失败: {e}")
    
    try:
        from florr_assistant.modules.pathing.navigator import Navigator
        print("✓ Navigator 导入成功")
    except Exception as e:
        errors.append(f"Navigator 导入失败: {e}")
        print(f"✗ Navigator 导入失败: {e}")
    
    try:
        from florr_assistant.modules.combat.target_selector import TargetSelector
        print("✓ TargetSelector 导入成功")
    except Exception as e:
        errors.append(f"TargetSelector 导入失败: {e}")
        print(f"✗ TargetSelector 导入失败: {e}")
    
    try:
        from florr_assistant.modules.combat.fighter import Fighter
        print("✓ Fighter 导入成功")
    except Exception as e:
        errors.append(f"Fighter 导入失败: {e}")
        print(f"✗ Fighter 导入失败: {e}")
    
    try:
        from florr_assistant.modules.stats.collector import StatsCollector
        print("✓ StatsCollector 导入成功")
    except Exception as e:
        errors.append(f"StatsCollector 导入失败: {e}")
        print(f"✗ StatsCollector 导入失败: {e}")
    
    print()
    print("=" * 50)
    print("测试模型文件...")
    print("=" * 50)
    
    models_dir = Path(__file__).parent.parent / "florr_assistant" / "models"
    
    model_files = {
        'afk-det.pt': models_dir / 'afk-det.pt',
        'afk-seg.pt': models_dir / 'afk-seg.pt',
        'mob_detector.pt': models_dir / 'mob_detector.pt',
    }
    
    for name, path in model_files.items():
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024) if path.is_file() else 0
            print(f"✓ {name} 存在 ({size_mb:.1f} MB)")
        else:
            errors.append(f"{name} 不存在")
            print(f"✗ {name} 不存在")
    
    maps_dir = Path(__file__).parent.parent / "florr-auto-pathing" / "maps"
    if maps_dir.exists():
        map_files = list(maps_dir.glob("*.png"))
        print(f"✓ 地图模板目录存在 ({len(map_files)} 个地图)")
    else:
        errors.append("地图模板目录不存在")
        print("✗ 地图模板目录不存在")
    
    print()
    print("=" * 50)
    print("测试结果")
    print("=" * 50)
    
    if errors:
        print(f"发现 {len(errors)} 个错误:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✓ 所有测试通过!")
        return True


def test_map_classifier():
    print()
    print("=" * 50)
    print("测试地图分类器...")
    print("=" * 50)
    
    try:
        from florr_assistant.modules.pathing.map_classifier import MapClassifier
        import cv2
        
        classifier = MapClassifier()
        
        test_image_path = Path(__file__).parent.parent / "florr-auto-pathing" / "map_dataset" / "真实游戏中garden的截图.png"
        
        if test_image_path.exists():
            image = cv2.imread(str(test_image_path))
            if image is not None:
                result = classifier.classify(image)
                print(f"✓ 地图分类测试成功:")
                print(f"  预测地图: {result['map']}")
                print(f"  置信度: {result['confidence']:.3f}")
                return True
            else:
                print("✗ 无法读取测试图片")
                return False
        else:
            print(f"✗ 测试图片不存在: {test_image_path}")
            return False
            
    except Exception as e:
        print(f"✗ 地图分类器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_app_initialization():
    print()
    print("=" * 50)
    print("测试应用初始化...")
    print("=" * 50)
    
    try:
        from florr_assistant.app import FlorrAssistant
        
        app = FlorrAssistant(headless=True)
        
        status = app.get_status()
        
        print(f"✓ 应用初始化成功")
        print(f"  平台: {status['platform'].get('system', 'unknown')}")
        print(f"  已注册模块: {len(status['modules'])}")
        
        for name, info in status['modules'].items():
            print(f"    - {name}: {info['state']}")
        
        return True
        
    except Exception as e:
        print(f"✗ 应用初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = True
    
    success = test_imports() and success
    success = test_map_classifier() and success
    success = test_app_initialization() and success
    
    print()
    print("=" * 50)
    if success:
        print("✓ 所有测试通过!")
    else:
        print("✗ 部分测试失败")
    print("=" * 50)
    
    sys.exit(0 if success else 1)
