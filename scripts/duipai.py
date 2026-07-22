#!/usr/bin/env python3
"""
OI.SKILL 本地对拍 / 样例测试脚本

用法：
  1. 对拍模式
     python3 duipai.py -s solution.cpp -b brute.cpp -g gen.py -n 100

  2. 样例测试模式
     python3 duipai.py -s solution.cpp -i sample.in -o sample.out

支持语言：C++(.cpp/.cc/.cxx)、Python(.py)、Java(.java)
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def detect_language(file_path):
    ext = Path(file_path).suffix.lower()
    if ext in (".cpp", ".cc", ".cxx"):
        return "cpp"
    if ext == ".py":
        return "python"
    if ext == ".java":
        return "java"
    raise ValueError(f"不支持的文件类型: {ext} ({file_path})")


def compile_source(file_path, work_dir):
    """编译源码，返回可执行文件路径或运行命令列表。"""
    lang = detect_language(file_path)
    basename = Path(file_path).stem

    if lang == "cpp":
        exe_path = os.path.join(work_dir, basename)
        cmd = ["g++", "-std=c++17", "-O2", "-o", exe_path, file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[编译错误] {file_path}")
            print(result.stderr)
            sys.exit(1)
        return [exe_path]

    if lang == "java":
        cmd = ["javac", "-d", work_dir, file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[编译错误] {file_path}")
            print(result.stderr)
            sys.exit(1)
        return ["java", "-cp", work_dir, basename]

    if lang == "python":
        return [sys.executable, file_path]

    raise ValueError(f"未知语言: {lang}")


def run_program(cmd, input_data, timeout):
    """运行程序，返回 (stdout, stderr, elapsed_ms, status)。"""
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = (time.perf_counter() - start) * 1000
        if proc.returncode != 0:
            return proc.stdout, proc.stderr, elapsed, "RE"
        return proc.stdout, proc.stderr, elapsed, "OK"
    except subprocess.TimeoutExpired as e:
        elapsed = (time.perf_counter() - start) * 1000
        return e.stdout or "", e.stderr or "", elapsed, "TLE"
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        return "", str(e), elapsed, "RE"


def normalize_output(text):
    """统一输出格式：去除首尾空白，保留行尾空格差异。"""
    lines = text.splitlines()
    lines = [line.rstrip() for line in lines]
    while lines and lines[-1] == "":
        lines.pop()
    while lines and lines[0] == "":
        lines.pop(0)
    return "\n".join(lines)


def run_sample_test(solution_cmd, sample_in, sample_out, timeout):
    """样例测试模式。"""
    with open(sample_in, "r", encoding="utf-8") as f:
        input_data = f.read()

    stdout, stderr, elapsed, status = run_program(solution_cmd, input_data, timeout)

    print(f"[样例测试] 输入: {sample_in}")
    print(f"[运行结果] 状态: {status} | 耗时: {elapsed:.1f} ms")

    if status != "OK":
        if stderr:
            print("[错误输出]")
            print(stderr)
        sys.exit(1)

    actual = normalize_output(stdout)

    if sample_out and os.path.exists(sample_out):
        with open(sample_out, "r", encoding="utf-8") as f:
            expected = normalize_output(f.read())
        if actual == expected:
            print("[结果] AC ✓")
            print("[输出]")
            print(actual)
        else:
            print("[结果] WA ✗")
            print("[你的输出]")
            print(actual)
            print("[期望输出]")
            print(expected)
            sys.exit(1)
    else:
        print("[结果] 已输出（无期望答案用于比对）")
        print("[输出]")
        print(actual)


def run_duipai(solution_cmd, brute_cmd, generator_cmd, runs, timeout):
    """对拍模式。"""
    print(f"[对拍] 总轮数: {runs} | 单轮超时: {timeout}s")

    for i in range(1, runs + 1):
        # 生成数据
        gen_out, gen_err, _, gen_status = run_program(generator_cmd, "", timeout)
        if gen_status != "OK":
            print(f"[第 {i} 轮] 数据生成器异常: {gen_status}")
            if gen_err:
                print(gen_err)
            sys.exit(1)

        test_data = gen_out

        # 运行待测程序
        sol_out, sol_err, sol_time, sol_status = run_program(solution_cmd, test_data, timeout)
        if sol_status != "OK":
            print(f"[第 {i} 轮] 待测程序 {sol_status} | 耗时: {sol_time:.1f} ms")
            print("[测试数据]")
            print(test_data)
            if sol_err:
                print("[错误输出]")
                print(sol_err)
            sys.exit(1)

        # 运行暴力程序
        brute_out, brute_err, brute_time, brute_status = run_program(brute_cmd, test_data, timeout)
        if brute_status != "OK":
            print(f"[第 {i} 轮] 暴力程序 {brute_status} | 耗时: {brute_time:.1f} ms")
            print("[测试数据]")
            print(test_data)
            if brute_err:
                print("[错误输出]")
                print(brute_err)
            sys.exit(1)

        sol_norm = normalize_output(sol_out)
        brute_norm = normalize_output(brute_out)

        if sol_norm != brute_norm:
            print(f"[第 {i} 轮] WA ✗")
            print("[测试数据]")
            print(test_data)
            print("[待测程序输出]")
            print(sol_norm)
            print(f"耗时: {sol_time:.1f} ms")
            print("[暴力程序输出]")
            print(brute_norm)
            print(f"耗时: {brute_time:.1f} ms")
            sys.exit(1)

        if i == 1 or i % 10 == 0 or i == runs:
            print(f"[第 {i} 轮] AC ✓ (sol {sol_time:.1f} ms, brute {brute_time:.1f} ms)")

    print(f"[对拍结束] 全部 {runs} 轮通过 ✓")


def main():
    parser = argparse.ArgumentParser(description="OI.SKILL 本地对拍 / 样例测试脚本")
    parser.add_argument("-s", "--solution", required=True, help="待测程序源文件路径")
    parser.add_argument("-b", "--brute", help="暴力程序源文件路径（对拍模式必填）")
    parser.add_argument("-g", "--generator", help="数据生成器源文件路径（对拍模式必填）")
    parser.add_argument("-i", "--sample", help="样例输入文件路径（样例测试模式）")
    parser.add_argument("-o", "--expected", help="期望输出文件路径（可选）")
    parser.add_argument("-n", "--runs", type=int, default=100, help="对拍轮数（默认 100）")
    parser.add_argument("-t", "--timeout", type=int, default=2, help="单轮运行超时秒数（默认 2）")
    args = parser.parse_args()

    if not os.path.exists(args.solution):
        print(f"[错误] 找不到待测程序: {args.solution}")
        sys.exit(1)

    work_dir = tempfile.mkdtemp(prefix="oi-skill-duipai-")
    try:
        solution_cmd = compile_source(args.solution, work_dir)

        if args.sample:
            # 样例测试模式
            if args.brute or args.generator:
                print("[警告] 样例测试模式下 --brute 和 --generator 将被忽略")
            run_sample_test(solution_cmd, args.sample, args.expected, args.timeout)
        else:
            # 对拍模式
            if not args.brute or not args.generator:
                print("[错误] 对拍模式需要同时提供 --brute 和 --generator")
                sys.exit(1)
            if not os.path.exists(args.brute):
                print(f"[错误] 找不到暴力程序: {args.brute}")
                sys.exit(1)
            if not os.path.exists(args.generator):
                print(f"[错误] 找不到数据生成器: {args.generator}")
                sys.exit(1)

            brute_cmd = compile_source(args.brute, work_dir)
            generator_cmd = compile_source(args.generator, work_dir)
            run_duipai(solution_cmd, brute_cmd, generator_cmd, args.runs, args.timeout)
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
