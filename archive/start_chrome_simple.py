#!/usr/bin/env python3
"""
🎯 简单的Chrome浏览器调试模式启动脚本
"""

import os
import platform
import subprocess
import time
import requests

def start_chrome_debug_simple():
    """简单的Chrome调试模式启动"""

    if platform.system() == 'Windows':
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        if not os.path.exists(chrome_path):
            print("❌ Chrome浏览器未找到")
            return False

        # 构建启动命令
        # 直接使用--remote-debugging-port参数
        command = f'"{chrome_path}" --remote-debugging-port=9222'

        print("🎯 正在启动Chrome调试模式...")
        print(f"📦 启动命令: {command}")

        try:
            # 使用subprocess.Popen启动Chrome
            process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True
            )

            print("✅ Chrome浏览器调试模式已启动")

            # 等待浏览器启动
            time.sleep(3)

            # 测试连接
            try:
                response = requests.get("http://localhost:9222/json", timeout=5)
                if response.status_code == 200:
                    print("✅ Chrome调试模式API接口连接成功")
                    return True
                else:
                    print(f"❌ Chrome调试模式API接口返回状态码: {response.status_code}")
                    return False

            except Exception as e:
                print(f"❌ 无法连接到Chrome调试模式API接口: {e}")
                return False

        except Exception as e:
            print(f"❌ 启动Chrome浏览器失败: {e}")
            return False

    else:
        print("❌ 该脚本仅支持Windows系统")
        return False

if __name__ == "__main__":
    start_chrome_debug_simple()