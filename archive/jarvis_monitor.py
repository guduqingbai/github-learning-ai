#!/usr/bin/env python3
"""
🚀 贾维斯主动沟通监控系统
持续运行的监控系统，定期检查是否需要主动沟通
"""

import os
import sys
import time
import threading
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jarvis_active import JarvisActiveCommunication


class JarvisMonitor:
    """
    贾维斯主动沟通监控系统
    """

    def __init__(self):
        """
        初始化监控系统
        """
        self.assistant: Optional[JarvisActiveCommunication] = None
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.check_interval = 60  # 检查间隔（秒）

    def _initialize_assistant(self):
        """
        初始化智能助手
        """
        try:
            self.assistant = JarvisActiveCommunication()
            return True
        except Exception as e:
            print(f"❌ 初始化助手失败: {e}")
            return False

    def _monitor_loop(self):
        """
        监控循环
        """
        print("🚀 监控系统启动")
        print(f"检查间隔: {self.check_interval}秒")
        print("=" * 60)

        while self.running:
            try:
                if not self.assistant:
                    if not self._initialize_assistant():
                        time.sleep(self.check_interval)
                        continue

                # 检查是否需要沟通
                if self.assistant.should_communicate():
                    self._handle_communication()

                # 等待下一次检查
                time.sleep(self.check_interval)

            except Exception as e:
                print(f"❌ 监控循环错误: {e}")
                time.sleep(self.check_interval)

        print("📴 监控系统停止")

    def _handle_communication(self):
        """
        处理用户响应
        """
        try:
            response = input("🧑 请输入您的响应: ").strip()
            self.assistant.handle_response(response)
        except KeyboardInterrupt:
            print("\n🔄 监控系统暂停")
            return
        except Exception as e:
            print(f"❌ 处理响应失败: {e}")

    def start(self):
        """
        启动监控系统
        """
        if self.running:
            print("⚠️  监控系统已经在运行")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()

        print("✅ 监控系统已启动")

    def stop(self):
        """
        停止监控系统
        """
        if not self.running:
            print("⚠️  监控系统已经停止")
            return

        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)

        if self.assistant:
            print("✅ 助手已停止")

        print("✅ 监控系统已停止")

    def force_communication(self):
        """
        强制进行主动沟通
        """
        if not self.assistant:
            if not self._initialize_assistant():
                return False

        return self.assistant.greet_and_ask()


def run_monitor():
    """
    运行监控系统
    """
    monitor = JarvisMonitor()

    print("🤖 贾维斯主动沟通监控系统")
    print("=" * 60)
    print("命令:")
    print("- 'c' 强制沟通")
    print("- 's' 停止监控")
    print("- 'q' 退出程序")
    print()

    try:
        monitor.start()

        while monitor.running:
            command = input("🔧 输入命令: ").strip().lower()

            if command == 'c':
                print()
                monitor.force_communication()
                monitor._handle_communication()
            elif command == 's':
                monitor.stop()
            elif command == 'q':
                monitor.stop()
                break
            else:
                print("❓ 未知命令，请使用 'c', 's', 或 'q'")

    except KeyboardInterrupt:
        print("\n📴 程序被中断")
        monitor.stop()
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        monitor.stop()


if __name__ == "__main__":
    run_monitor()
