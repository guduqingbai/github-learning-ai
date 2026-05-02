#!/usr/bin/env python3
"""
🎯 Chrome浏览器调试模式启动脚本
"""

import os
import platform
import subprocess
import time
import requests

def start_chrome_debug():
    """启动Chrome浏览器调试模式"""

    if platform.system() == 'Windows':
        # Windows系统Chrome路径
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        if not os.path.exists(chrome_path):
            print("❌ Chrome浏览器未找到")
            return False

        # 启动Chrome浏览器调试模式
        print("🎯 正在启动Chrome浏览器调试模式...")
        try:
            # 使用--remote-debugging-port=9222启动Chrome调试模式
            command = [
                chrome_path,
                "--remote-debugging-port=9222",
                "--no-first-run",
                "--no-default-browser-check"
            ]

            # 启动Chrome进程
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
                response = requests.get("http://localhost:9222/json", timeout=2)
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

    elif platform.system() == 'Darwin':
        # macOS系统
        print("⚠️ macOS系统Chrome调试模式需要手动启动")
        return False

    else:
        # Linux系统
        print("⚠️ Linux系统Chrome调试模式需要手动启动")
        return False

if __name__ == "__main__":
    start_chrome_debug()