"""命令行入口"""
import argparse
from . import MobWikiMonitor


def main():
    parser = argparse.ArgumentParser(description="Florr.io Mob维基监测器")
    parser.add_argument("--check", action="store_true", help="仅检查新mob，不下载")
    parser.add_argument("--download", action="store_true", help="检查并下载新mob图片")
    parser.add_argument("--status", action="store_true", help="显示当前状态")
    parser.add_argument("-q", "--quiet", action="store_true", help="静默模式")
    
    args = parser.parse_args()
    
    monitor = MobWikiMonitor(verbose=not args.quiet)
    
    if args.status:
        status = monitor.get_status()
        print(f"\n本地mob数量: {status['local_mobs_count']}")
        print(f"已知mob数量: {status['known_mobs_count']}")
        if not args.quiet:
            print(f"\n本地mob列表:\n{', '.join(status['local_mobs'])}")
    
    elif args.check:
        result = monitor.check_updates()
        print(f"\n维基mob总数: {result['total_wiki_mobs']}")
        print(f"本地mob总数: {result['total_local_mobs']}")
        print(f"新增mob数量: {len(result['new_mobs'])}")
        if result['new_mobs']:
            print("\n新增mob列表:")
            for mob in result['new_mobs']:
                print(f"  - {mob['name']} ({mob['normalized_name']})")
    
    elif args.download:
        result = monitor.run()
        print(f"\n下载完成: {len(result['download']['downloaded'])} 个")
        print(f"下载失败: {len(result['download']['failed'])} 个")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
