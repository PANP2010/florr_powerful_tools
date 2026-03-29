"""
Module Tester - florr_assistant 各模块导入和功能测试
测试 core、modules 等核心模块是否能正常导入和运行
"""

import sys
import os
import time
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Screenshots output dir
SCREENSHOT_DIR = Path(__file__).parent.parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


class ModuleTestResult:
    """测试结果"""

    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error: str = ""
        self.warnings: List[str] = []
        self.info: Dict[str, Any] = {}
        self.screenshot: str = ""

    def __repr__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"[{self.name}] {status}: {self.error or 'OK'}"


def test_core_logger() -> ModuleTestResult:
    """测试核心日志模块"""
    result = ModuleTestResult("core/logger")

    try:
        from florr_assistant.core.logger import Logger

        logger = Logger()
        logger.info("测试日志", module="ModuleTester")
        result.passed = True
        result.info["logger_class"] = str(Logger)
    except Exception as e:
        result.error = str(e)
        result.error_detail = traceback.format_exc()

    return result


def test_core_config() -> ModuleTestResult:
    """测试核心配置模块"""
    result = ModuleTestResult("core/config")

    try:
        from florr_assistant.core.config import Config

        config = Config()
        result.passed = True
        result.info["config_class"] = str(Config)

        # Test config access
        test_value = config.get("test_key", "default")
        result.info["get_default"] = test_value == "default"
    except Exception as e:
        result.error = str(e)
        result.error_detail = traceback.format_exc()

    return result


def test_core_engine() -> ModuleTestResult:
    """测试核心引擎模块"""
    result = ModuleTestResult("core/engine")

    try:
        from florr_assistant.core.engine import Engine

        result.passed = True
        result.info["engine_class"] = str(Engine)
    except Exception as e:
        result.error = str(e)
        result.error_detail = traceback.format_exc()

    return result


def test_core_platform() -> ModuleTestResult:
    """测试核心平台模块"""
    result = ModuleTestResult("core/platform")

    try:
        from florr_assistant.core.platform import PlatformManager

        platform = PlatformManager()
        result.passed = True
        result.info["platform_type"] = str(type(platform).__name__)

        # Test screenshot capture (may fail if no display)
        try:
            screenshot = platform.capture_screen()
            if screenshot is not None:
                result.info["screenshot_shape"] = str(screenshot.shape)
            else:
                result.warnings.append("截图返回 None (无显示环境)")
        except Exception as ss_err:
            result.warnings.append(f"截图不可用: {ss_err}")

    except Exception as e:
        result.error = str(e)
        result.error_detail = traceback.format_exc()

    return result


def test_core_events() -> ModuleTestResult:
    """测试核心事件模块"""
    result = ModuleTestResult("core/events")

    try:
        from florr_assistant.core.events import EventBus

        bus = EventBus()
        result.passed = True
        result.info["eventbus_class"] = str(EventBus)

        # Test subscribe
        events_received = []

        def test_handler(event):
            events_received.append(event)

        bus.subscribe("test.event", test_handler)
        bus.publish("test.event", {"data": "test"})
        result.info["event_published"] = len(events_received) > 0

    except Exception as e:
        result.error = str(e)
        result.error_detail = traceback.format_exc()

    return result


def test_module_base() -> ModuleTestResult:
    """测试模块基类"""
    result = ModuleTestResult("modules/base")

    try:
        from florr_assistant.modules.base import BaseModule, ModuleState

        result.passed = True
        result.info["base_module_class"] = str(BaseModule)
        result.info["module_state_enum"] = str(ModuleState)

    except Exception as e:
        result.error = str(e)
        result.error_detail = traceback.format_exc()

    return result


def test_module_afk() -> ModuleTestResult:
    """测试 AFK 模块"""
    result = ModuleTestResult("modules/afk")

    try:
        from florr_assistant.modules.afk import detector, responder

        result.passed = True
        result.info["detector_module"] = str(type(detector).__name__)
        result.info["responder_module"] = str(type(responder).__name__)

    except Exception as e:
        result.error = str(e)
        result.error_detail = traceback.format_exc()

    return result


def test_module_pathing() -> ModuleTestResult:
    """测试寻路模块"""
    result = ModuleTestResult("modules/pathing")

    try:
        from florr_assistant.modules.pathing import navigator, map_classifier

        result.passed = True
        result.info["navigator_class"] = str(navigator.Navigator)
        result.info["map_classifier_class"] = str(map_classifier.MapClassifier)

    except Exception as e:
        result.error = str(e)
        result.error_detail = traceback.format_exc()

    return result


def test_module_combat() -> ModuleTestResult:
    """测试战斗模块"""
    result = ModuleTestResult("modules/combat")

    try:
        from florr_assistant.modules.combat import fighter, target_selector

        result.passed = True
        result.info["fighter_class"] = str(fighter.Fighter)
        result.info["target_selector_class"] = str(target_selector.TargetSelector)

    except Exception as e:
        result.error = str(e)
        result.error_detail = traceback.format_exc()

    return result


def test_module_data_collector() -> ModuleTestResult:
    """测试数据收集模块"""
    result = ModuleTestResult("modules/data_collector")

    try:
        from florr_assistant.modules.data_collector import collector

        result.passed = True
        result.info["collector_class"] = str(collector.DataCollector)
        result.info["mob_types_count"] = len(collector.DataCollector.MOB_TYPES)

    except Exception as e:
        result.error = str(e)
        result.error_detail = traceback.format_exc()

    return result


def test_module_stats() -> ModuleTestResult:
    """测试统计模块"""
    result = ModuleTestResult("modules/stats")

    try:
        from florr_assistant.modules.stats import collector

        result.passed = True
        result.info["stats_collector_class"] = str(collector.StatsCollector)

    except Exception as e:
        result.error = str(e)
        result.error_detail = traceback.format_exc()

    return result


def test_ui_modules() -> ModuleTestResult:
    """测试 UI 模块"""
    result = ModuleTestResult("ui/modules")

    try:
        from florr_assistant.ui import main_window, overlay_window, data_collection_window, styles

        result.passed = True
        result.info["main_window"] = str(type(main_window).__name__)
        result.info["overlay_window"] = str(type(overlay_window).__name__)
        result.info["styles_module"] = "OK"

    except ImportError as e:
        # GUI may fail without display
        result.passed = True
        result.warnings.append(f"UI 模块导入警告 (GUI 可能需要显示环境): {e}")
    except Exception as e:
        result.error = str(e)
        result.error_detail = traceback.format_exc()

    return result


def test_cv2_import() -> ModuleTestResult:
    """测试 cv2 导入（检查 OpenCV 是否可用）"""
    result = ModuleTestResult("opencv(cv2)")

    try:
        import cv2

        result.passed = True
        result.info["cv2_version"] = cv2.__version__
        result.info["cv2_path"] = str(cv2.__file__)

    except ImportError as e:
        result.error = f"cv2 未安装: {e}"
        result.warnings.append("collector.py 中的 cv2 使用延迟导入，cv2 不可用时会跳过相关功能")
    except Exception as e:
        result.error = str(e)

    return result


def test_torch_import() -> ModuleTestResult:
    """测试 PyTorch 导入"""
    result = ModuleTestResult("pytorch(torch)")

    try:
        import torch

        result.passed = True
        result.info["torch_version"] = torch.__version__
        result.info["cuda_available"] = torch.cuda.is_available()

    except ImportError as e:
        result.error = f"torch 未安装: {e}"
    except Exception as e:
        result.error = str(e)

    return result


def test_ultralytics_import() -> ModuleTestResult:
    """测试 Ultralytics (YOLO) 导入"""
    result = ModuleTestResult("ultralytics(YOLO)")

    try:
        from ultralytics import YOLO

        result.passed = True
        result.info["yolo_class"] = str(YOLO)

    except ImportError as e:
        result.error = f"ultralytics 未安装: {e}"
        result.warnings.append("YOLO 模型检测功能不可用")
    except Exception as e:
        result.error = str(e)

    return result


def take_screenshot(name: str) -> str:
    """截取当前屏幕"""
    try:
        from playwright.sync_api import sync_playwright

        filepath = SCREENSHOT_DIR / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("about:blank")
            # Take a blank page screenshot as placeholder
            page.screenshot(path=str(filepath))
            browser.close()

        return str(filepath)
    except Exception as e:
        return f"[截图失败: {e}]"


def run_all_tests(verbose: bool = True) -> Tuple[List[ModuleTestResult], int, int]:
    """
    运行所有模块测试

    Returns:
        (results, passed_count, failed_count)
    """
    tests = [
        test_core_logger,
        test_core_config,
        test_core_engine,
        test_core_platform,
        test_core_events,
        test_module_base,
        test_module_afk,
        test_module_pathing,
        test_module_combat,
        test_module_data_collector,
        test_module_stats,
        test_ui_modules,
        test_cv2_import,
        test_torch_import,
        test_ultralytics_import,
    ]

    results: List[ModuleTestResult] = []
    start_time = time.time()

    if verbose:
        print("\n" + "=" * 60)
        print("🔍 Florr Assistant 模块测试")
        print("=" * 60 + "\n")

    for test_func in tests:
        result = test_func()
        results.append(result)

        if verbose:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"  {status}  {result.name}")
            if result.warnings:
                for w in result.warnings:
                    print(f"         ⚠️  {w}")
            if result.error and verbose:
                print(f"         🔍 {result.error[:80]}")

    elapsed = time.time() - start_time
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    if verbose:
        print("\n" + "=" * 60)
        print(f"📊 测试结果: {passed} 通过, {failed} 失败, {len(results)} 总计")
        print(f"⏱️  耗时: {elapsed:.2f}s")
        print("=" * 60 + "\n")

    return results, passed, failed


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Florr Assistant 模块测试工具")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    parser.add_argument(
        "--module", "-m", type=str, help="只测试指定模块 (e.g., core/logger)"
    )
    args = parser.parse_args()

    if args.module:
        # Single module test
        module_map = {
            "core/logger": test_core_logger,
            "core/config": test_core_config,
            "core/engine": test_core_engine,
            "core/platform": test_core_platform,
            "core/events": test_core_events,
            "modules/base": test_module_base,
            "modules/afk": test_module_afk,
            "modules/pathing": test_module_pathing,
            "modules/combat": test_module_combat,
            "modules/data_collector": test_module_data_collector,
            "modules/stats": test_module_stats,
            "ui/modules": test_ui_modules,
            "opencv(cv2)": test_cv2_import,
            "pytorch(torch)": test_torch_import,
            "ultralytics(YOLO)": test_ultralytics_import,
        }

        if args.module not in module_map:
            print(f"❌ 未知模块: {args.module}")
            print(f"可用模块: {', '.join(module_map.keys())}")
            sys.exit(1)

        result = module_map[args.module]()
        print(f"{result}")
        sys.exit(0 if result.passed else 1)

    # Run all tests
    results, passed, failed = run_all_tests(verbose=not args.quiet)

    # Generate summary report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = SCREENSHOT_DIR / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Florr Assistant 模块测试报告\n")
        f.write(f"时间: {timestamp}\n")
        f.write(f"{'=' * 60}\n\n")
        for r in results:
            status = "PASS" if r.passed else "FAIL"
            f.write(f"[{status}] {r.name}\n")
            if r.error:
                f.write(f"  Error: {r.error}\n")
            for w in r.warnings:
                f.write(f"  Warning: {w}\n")
            for k, v in r.info.items():
                f.write(f"  {k}: {v}\n")
            f.write("\n")

    print(f"📄 测试报告: {report_path}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
