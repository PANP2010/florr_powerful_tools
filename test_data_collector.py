#!/usr/bin/env python3
"""
test_data_collector.py - 测试数据收集器
Agent 通过调用此脚本获取模块测试数据
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PYTHON = "/home/kuli/.openclaw/deer-flow/backend/.venv/bin/python"
TEST_DIR = Path("/home/kuli/florr_powerful_tools/tests")
OUT_FILE = Path("/tmp/florr_test_data.json")


def run_tests(module: str = None, verbose: bool = False) -> dict:
    """运行测试并收集数据"""
    start = time.time()
    
    cmd = [PYTHON, "-m", "pytest"]
    if verbose:
        cmd.append("-v")
    cmd.append("--tb=short")
    cmd.append("--json-report")
    cmd.append(f"--json-report-file={OUT_FILE}")
    
    if module:
        cmd.append(f"{TEST_DIR}/{module}")
    else:
        cmd.append(str(TEST_DIR))
    
    result = subprocess.run(cmd, capture_output=True, text=True, 
                            cwd="/home/kuli/florr_powerful_tools")
    
    duration = time.time() - start
    
    # 解析 pytest 输出
    output = result.stdout + result.stderr
    
    passed = failed = skipped = errors = 0
    for line in output.split("\n"):
        if "passed" in line:
            passed = int(output.split("passed")[0].strip().split()[-1])
        if "failed" in line:
            failed = int(output.split("failed")[0].strip().split()[-1])
        if "skipped" in line:
            skipped = int(output.split("skipped")[0].strip().split()[-1])
    
    # 读取 JSON 报告（如果存在）
    test_results = []
    if OUT_FILE.exists():
        try:
            with open(OUT_FILE) as f:
                report = json.load(f)
                test_results = report.get("results", [])
        except:
            pass
    
    return {
        "timestamp": datetime.now().isoformat(),
        "module": module or "all",
        "status": "passed" if result.returncode == 0 else "failed",
        "duration_s": round(duration, 2),
        "summary": {
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors
        },
        "test_results": test_results[:20],  # 最多20条详细结果
        "exit_code": result.returncode,
        "raw_output": output[-2000:]  # 最后2000字符
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Florr 测试数据收集器")
    parser.add_argument("--module", "-m", help="指定测试模块 (e.g., test_engine.py)")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 输出")
    parser.add_argument("--report", "-r", help="输出报告文件路径")
    args = parser.parse_args()
    
    data = run_tests(module=args.module, verbose=args.verbose or args.json)
    
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"[{data['timestamp']}] {'✅' if data['status']=='passed' else '❌'} {data['module']}")
        print(f"   通过: {data['summary']['passed']}  失败: {data['summary']['failed']}  跳过: {data['summary']['skipped']}")
        print(f"   耗时: {data['duration_s']}s")
    
    if args.report:
        with open(args.report, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"报告已保存: {args.report}")


if __name__ == "__main__":
    main()
