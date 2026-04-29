#!/usr/bin/env python3
"""
⏱️  精确时间测量工具
提供任务执行时间的精确测量和报告功能
"""

import time
import functools
import json
from pathlib import Path
from datetime import datetime

class Timer:
    """
    精确时间测量器
    """

    def __init__(self, task_name=""):
        self.task_name = task_name
        self.start_time = 0
        self.end_time = 0
        self.duration = 0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time

    @property
    def seconds(self):
        return self.duration

    @property
    def milliseconds(self):
        return self.duration * 1000

    @property
    def microseconds(self):
        return self.duration * 1000000

    def format(self, precision=2):
        """格式化输出时间"""
        if self.duration < 0.001:
            return f"{self.microseconds:.0f}μs"
        elif self.duration < 1.0:
            return f"{self.milliseconds:.1f}ms"
        else:
            return f"{self.seconds:.{precision}f}秒"

    def __str__(self):
        return self.format()


def timed(task_name=""):
    """
    装饰器：测量函数执行时间

    Args:
        task_name: 任务名称

    Returns:
        装饰后的函数
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timer = Timer(task_name or func.__name__)
            with timer:
                result = func(*args, **kwargs)

            print(f"⏱️  {timer.task_name or func.__name__}: {timer}")
            return result
        return wrapper
    return decorator


class TimeReporter:
    """
    时间报告器
    """

    def __init__(self):
        self.tasks = []

    def add_task(self, task_name, duration):
        """
        添加任务时间

        Args:
            task_name: 任务名称
            duration: 持续时间（秒）
        """
        self.tasks.append({
            "task_name": task_name,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })

    def get_summary(self):
        """
        获取时间统计摘要

        Returns:
            时间统计字典
        """
        total_duration = sum(task["duration"] for task in self.tasks)
        avg_duration = total_duration / len(self.tasks) if self.tasks else 0

        return {
            "total_tasks": len(self.tasks),
            "total_duration": total_duration,
            "avg_duration": avg_duration,
            "tasks": [
                {
                    "name": task["task_name"],
                    "duration": task["duration"],
                    "percentage": (task["duration"] / total_duration * 100) if total_duration > 0 else 0
                }
                for task in sorted(self.tasks, key=lambda x: x["duration"], reverse=True)
            ]
        }

    def print_summary(self):
        """打印时间统计摘要"""
        summary = self.get_summary()

        print("\n⏱️  任务执行时间统计")
        print("=" * 50)

        total_duration = Timer("Total").format(2)
        avg_duration = Timer("Avg").format(2)

        print(f"📊 总任务数: {summary['total_tasks']}个")
        print(f"⏰ 总时间: {summary['total_duration']:.2f}秒")
        print(f"📈 平均时间: {summary['avg_duration']:.2f}秒")
        print()

        for task in summary["tasks"]:
            percentage = f"({task['percentage']:.1f}%)"
            duration = f"{task['duration']:.3f}秒"
            print(f"🔹 {task['name']}: {duration:<10} {percentage}")

    def save_to_file(self, filename="timing_report.json"):
        """保存时间报告到文件"""
        report = self.get_summary()
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    def load_from_file(self, filename="timing_report.json"):
        """从文件加载时间报告"""
        if Path(filename).exists():
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        return None


# 全局时间报告器实例
global_reporter = TimeReporter()


def measure_performance(func):
    """
    装饰器：测量性能并添加到全局报告器

    Args:
        func: 要测量的函数

    Returns:
        装饰后的函数
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        timer = Timer(func.__name__)
        with timer:
            result = func(*args, **kwargs)

        global_reporter.add_task(func.__name__, timer.duration)
        print(f"⏱️  {func.__name__}: {timer.format()}")
        return result
    return wrapper


# 简单的性能测试函数
def performance_test():
    """性能测试函数"""

    @measure_performance
    def sleep_test():
        time.sleep(0.1)

    @measure_performance
    def calculation_test():
        result = 0
        for i in range(1000000):
            result += i
        return result

    @measure_performance
    def io_test():
        filename = "test.tmp"
        with open(filename, "w") as f:
            for i in range(100):
                f.write(f"Line {i}\n")

        with open(filename, "r") as f:
            content = f.read()

        import os
        os.remove(filename)
        return len(content)

    sleep_test()
    calculation_test()
    io_test()

    print()
    global_reporter.print_summary()

    return global_reporter.get_summary()


if __name__ == "__main__":
    print("🎯 精确时间测量工具测试")
    print("=" * 50)

    performance_test()