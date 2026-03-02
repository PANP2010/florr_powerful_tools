import sys
import platform

def check_dependencies():
    print("检查依赖...")
    
    try:
        import PyQt5
        print("✓ PyQt5 已安装")
    except ImportError:
        print("✗ PyQt5 未安装")
        print("请运行: pip install PyQt5")
        return False
    
    return True

def main():
    if not check_dependencies():
        sys.exit(1)
    
    print(f"系统: {platform.system()}")
    print(f"Python 版本: {sys.version}")
    
    from game_overlay_ui import main as ui_main
    
    try:
        ui_main()
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()