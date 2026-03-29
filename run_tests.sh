#!/bin/bash
# run_tests.sh - 运行 florr_powerful_tools 测试并生成报告
# 使用方法: ./run_tests.sh [--module MODULE] [--verbose] [--json]

set -e
PYTHON="/home/kuli/.openclaw/deer-flow/backend/.venv/bin/python"
TEST_DIR="/home/kuli/florr_powerful_tools/tests"
REPORT_FILE="/tmp/florr_test_report_$(date +%Y%m%d_%H%M%S).json"
VERBOSE=""
MODULE=""
JSON_OUTPUT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --module)
            MODULE="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE="-v"
            shift
            ;;
        --json)
            JSON_OUTPUT="--json-report"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--module MODULE] [--verbose] [--json]"
            echo "  --module  MODULE   只测试指定模块 (e.g., test_engine.py)"
            echo "  --verbose         详细输出"
            echo "  --json            生成 JSON 格式报告"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

cd /home/kuli/florr_powerful_tools

echo "[run_tests] 开始测试..."
echo "[run_tests] Python: $($PYTHON --version)"

if [ -n "$MODULE" ]; then
    TARGET="$TEST_DIR/$MODULE"
    echo "[run_tests] 测试模块: $MODULE"
else
    TARGET="$TEST_DIR/"
    echo "[run_tests] 测试全部模块"
fi

# 生成 JSON 报告
if [ -n "$JSON_OUTPUT" ]; then
    $PYTHON -m pytest $TARGET $VERBOSE --json-report --json-report-file="$REPORT_FILE" 2>&1
    echo "[run_tests] JSON 报告: $REPORT_FILE"
else
    $PYTHON -m pytest $TARGET $VERBOSE --tb=short 2>&1
fi

# 测试统计
echo ""
echo "=== 测试摘要 ==="
$PYTHON -m pytest $TARGET --tb=no -q 2>&1 | tail -5
echo "=== 测试完成 ==="
