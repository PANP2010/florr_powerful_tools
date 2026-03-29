"""
Screenshot Tester - 浏览器截图测试工具
使用 Playwright (headless Chromium) 截取页面截图
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright


def screenshot_test(url: str, name: str, output_dir: str = "screenshots", delay: float = 2.0) -> bool:
    """
    截取指定 URL 的截图

    Args:
        url: 目标 URL
        name: 保存文件名（不含扩展名）
        output_dir: 输出目录
        delay: 等待加载的延迟（秒）

    Returns:
        是否成功
    """
    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})

            print(f"[Screenshot] 正在访问: {url}")
            page.goto(url, timeout=30000, wait_until="networkidle")

            time.sleep(delay)

            filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(output_dir, filename)

            page.screenshot(path=filepath, full_page=False)
            browser.close()

            print(f"[Screenshot] ✅ 保存成功: {filepath}")
            return True

        except Exception as e:
            print(f"[Screenshot] ❌ 错误: {e}")
            if browser:
                browser.close()
            return False


def screenshot_local_file(filepath: str, name: str, output_dir: str = "screenshots") -> bool:
    """
    截取本地 HTML 文件的截图

    Args:
        filepath: 本地文件路径
        name: 保存文件名
        output_dir: 输出目录

    Returns:
        是否成功
    """
    if not os.path.exists(filepath):
        print(f"[Screenshot] ❌ 文件不存在: {filepath}")
        return False

    file_url = f"file://{os.path.abspath(filepath)}"
    return screenshot_test(file_url, name, output_dir)


def screenshot_florr_io(test_mode: bool = False, output_dir: str = "screenshots") -> bool:
    """
    截取 florr.io 游戏页面的截图

    Args:
        test_mode: 是否使用测试模式
        output_dir: 输出目录

    Returns:
        是否成功
    """
    url = "https://florr.io" if not test_mode else "https://test.florrio.com"
    name = "florr_main" if not test_mode else "florr_test"

    print(f"[Florr] 截取 florr.io 截图...")
    return screenshot_test(url, name, output_dir, delay=3.0)


def batch_screenshot(urls: list, output_dir: str = "screenshots") -> dict:
    """
    批量截取多个 URL 的截图

    Args:
        urls: URL 列表 [(url, name), ...]
        output_dir: 输出目录

    Returns:
        结果字典
    """
    results = {}
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    batch_dir = os.path.join(output_dir, f"batch_{timestamp}")
    os.makedirs(batch_dir, exist_ok=True)

    print(f"[Batch] 开始批量截图，共 {len(urls)} 个 URL...")
    print(f"[Batch] 输出目录: {batch_dir}")

    for i, (url, name) in enumerate(urls):
        print(f"[Batch] [{i+1}/{len(urls)}] {url}")
        success = screenshot_test(url, name, batch_dir, delay=2.0)
        results[url] = success

    success_count = sum(1 for v in results.values() if v)
    print(f"[Batch] ✅ 完成: {success_count}/{len(urls)} 成功")

    return results


def main():
    parser = argparse.ArgumentParser(description="Florr 浏览器截图测试工具")
    parser.add_argument("--url", "-u", type=str, help="目标 URL")
    parser.add_argument("--name", "-n", type=str, default="screenshot", help="保存文件名")
    parser.add_argument("--output", "-o", type=str, default="screenshots", help="输出目录")
    parser.add_argument("--delay", "-d", type=float, default=2.0, help="加载延迟（秒）")
    parser.add_argument("--florr", "-f", action="store_true", help="截取 florr.io 截图")
    parser.add_argument("--test", "-t", action="store_true", help="使用测试模式")
    parser.add_argument("--file", type=str, help="本地 HTML 文件路径")

    args = parser.parse_args()

    if args.florr:
        success = screenshot_florr_io(test_mode=args.test, output_dir=args.output)
        sys.exit(0 if success else 1)

    if args.file:
        success = screenshot_local_file(args.file, args.name, args.output)
        sys.exit(0 if success else 1)

    if args.url:
        success = screenshot_test(args.url, args.name, args.output, args.delay)
        sys.exit(0 if success else 1)

    # Default: 演示模式
    demo_urls = [
        ("https://florr.io", "florr_io"),
        ("https://github.com", "github"),
    ]
    results = batch_screenshot(demo_urls, args.output)
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
