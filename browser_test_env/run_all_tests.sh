#!/bin/bash
# ============================================================
# Florr Powerful Tools - 完整测试套件
# 运行所有测试: 截图测试 + 模块测试
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  🚀 Florr Powerful Tools - 完整测试套件${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# 创建截图目录
echo -e "${YELLOW}[1/3]${NC} 创建截图目录..."
mkdir -p screenshots
echo "✅ 截图目录: screenshots/"

# 使用项目虚拟环境的 Python
PYTHON="$PROJECT_ROOT/.venv/bin/python"
if [ ! -x "$PYTHON" ]; then
    PYTHON="python3"
fi

# 检查 Playwright
echo ""
echo -e "${YELLOW}[2/3]${NC} 运行截图测试 (screenshot_tester.py)..."
echo "---------------------------------------------------"
if "$PYTHON" -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    "$PYTHON" "$SCRIPT_DIR/screenshot_tester.py" --florr 2>&1 || true
    echo "✅ 截图测试完成 (screenshots/ 目录)"
else
    echo -e "${YELLOW}⚠️  Playwright 未安装，跳过截图测试${NC}"
    echo "   安装命令: pip install playwright && python -m playwright install chromium"
fi

# 运行模块测试
echo ""
echo -e "${YELLOW}[3/3]${NC} 运行模块测试 (module_tester.py)..."
echo "---------------------------------------------------"
"$PYTHON" "$SCRIPT_DIR/module_tester.py" --quiet

# 测试结果汇总
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  📊 测试完成${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "查看详细报告: screenshots/test_report_*.txt"
echo "查看截图: screenshots/*.png"
echo ""
