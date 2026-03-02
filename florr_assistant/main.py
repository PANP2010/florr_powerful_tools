"""
Florr Assistant - 主入口
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from florr_assistant.app import FlorrAssistant


def parse_args():
    parser = argparse.ArgumentParser(
        description='Florr Assistant - 智能florr.io游戏辅助工具'
    )
    parser.add_argument(
        '-c', '--config',
        type=str,
        default=None,
        help='配置文件路径'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='无界面模式运行'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出'
    )
    parser.add_argument(
        '--start-all',
        action='store_true',
        help='启动时自动开始所有模块'
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    app = FlorrAssistant(
        config_path=args.config,
        headless=args.headless,
    )
    
    if args.verbose:
        app.logger.set_level('DEBUG')
    
    if args.start_all:
        app.start_all()
    
    try:
        app.run()
    except KeyboardInterrupt:
        print('\n正在退出...')
        app.shutdown()
    except Exception as e:
        print(f'错误: {e}')
        app.shutdown()
        sys.exit(1)


if __name__ == '__main__':
    main()
