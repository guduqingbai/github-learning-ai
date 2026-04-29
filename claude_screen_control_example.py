#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude辅助的屏幕识别和鼠标操作示例
"""

import pyautogui
from PIL import ImageGrab
import time

def click_button_by_image(image_path, confidence=0.8):
    """通过图像识别点击按钮"""
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            pyautogui.moveTo(location, duration=0.5)
            pyautogui.click()
            return True
        return False
    except Exception as e:
        print(f"❌ 点击失败: {e}")
        return False

def capture_and_analyze_region(x1, y1, x2, y2):
    """捕捉屏幕区域并分析"""
    try:
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        screenshot.save(f"screenshot_{int(time.time())}.png")
        return True
    except Exception as e:
        print(f"❌ 捕捉失败: {e}")
        return False

def main():
    print("🚀 Claude辅助操作演示")
    
    # 示例：点击浏览器地址栏并导航到GitHub
    print("📝 点击地址栏")
    if click_button_by_image("address_bar.png"):
        pyautogui.write("https://github.com", interval=0.1)
        pyautogui.press("enter")
        print("✅ 导航成功")
    
    print("
✅ 演示完成")

if __name__ == "__main__":
    main()
