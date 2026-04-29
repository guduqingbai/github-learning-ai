#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第2小时 - PyAutoGUI基础练习脚本
演示PyAutoGUI的基本功能，包括鼠标和键盘操作
"""

import pyautogui
import time
import sys


def show_safe_warning():
    """显示安全警告"""
    print("⚠️  安全警告")
    print("-" * 60)
    print("1. 此脚本将控制鼠标和键盘")
    print("2. 如遇到问题，请快速将鼠标移动到屏幕角落")
    print("3. PyAutoGUI将停止操作")
    print("4. 或按Ctrl+C在终端中断")
    print("-" * 60)

    time.sleep(3)


def get_screen_info():
    """获取屏幕信息"""
    print("\n📊 屏幕信息")
    print("=" * 60)

    width, height = pyautogui.size()
    print(f"🖥️  屏幕分辨率: {width}x{height}")

    x, y = pyautogui.position()
    print(f"🖱️  鼠标当前位置: ({x}, {y})")

    return width, height


def mouse_basic_operations():
    """基础鼠标操作"""
    print("\n🖱️  基础鼠标操作")
    print("=" * 60)

    # 获取屏幕中心位置
    center_x, center_y = pyautogui.size()
    center_x //= 2
    center_y //= 2

    print(f"🎯 移动到屏幕中心: ({center_x}, {center_y})")
    pyautogui.moveTo(center_x, center_y, duration=1)
    time.sleep(1)

    print("🔴 点击操作")
    pyautogui.click()
    time.sleep(0.5)

    print("🟢 双击操作")
    pyautogui.doubleClick()
    time.sleep(1)

    print("🔵 右键点击")
    pyautogui.rightClick()
    time.sleep(1)

    print("✅ 基础鼠标操作完成")


def mouse_drag_operations():
    """鼠标拖拽操作"""
    print("\n🎯 鼠标拖拽操作")
    print("=" * 60)

    center_x, center_y = pyautogui.size()
    center_x //= 2
    center_y //= 2

    start_x, start_y = center_x - 100, center_y - 100
    end_x, end_y = center_x + 100, center_y + 100

    print(f"📏 从 ({start_x}, {start_y}) 拖拽到 ({end_x}, {end_y})")
    pyautogui.moveTo(start_x, start_y, duration=0.5)
    pyautogui.dragTo(end_x, end_y, duration=1, button='left')
    time.sleep(1)

    print("✅ 拖拽操作完成")


def keyboard_operations():
    """键盘操作"""
    print("\n⌨️  键盘操作")
    print("=" * 60)

    # 测试文字输入
    print("📝 文字输入测试")
    pyautogui.write("Hello, PyAutoGUI!", interval=0.1)
    time.sleep(1)

    # 测试特殊键
    print("🔑 特殊键测试")
    pyautogui.press('enter')
    time.sleep(0.5)

    print("📝 多行文字输入")
    pyautogui.write("\nPyAutoGUI is powerful!", interval=0.1)
    pyautogui.press('enter')
    time.sleep(1)

    print("✅ 键盘操作完成")


def hotkey_operations():
    """热键操作"""
    print("\n🔥 热键操作")
    print("=" * 60)

    # 常用热键
    print("📋 复制操作 (Ctrl+C)")
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)

    print("📋 剪切操作 (Ctrl+X)")
    pyautogui.hotkey('ctrl', 'x')
    time.sleep(0.5)

    print("📋 粘贴操作 (Ctrl+V)")
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)

    print("✅ 热键操作完成")


def scroll_operations():
    """滚动操作"""
    print("\n🔄 滚动操作")
    print("=" * 60)

    print("⬇️  向下滚动")
    pyautogui.scroll(-50)
    time.sleep(0.5)

    print("⬆️  向上滚动")
    pyautogui.scroll(50)
    time.sleep(0.5)

    print("✅ 滚动操作完成")


def main():
    """主函数"""
    print("🚀 第2小时 - PyAutoGUI基础练习")
    print("=" * 60)

    try:
        show_safe_warning()
        get_screen_info()
        mouse_basic_operations()
        mouse_drag_operations()
        keyboard_operations()
        hotkey_operations()
        scroll_operations()

        print("\n🎉 所有基础操作练习完成！")
        print("\n📋 已学习的操作:")
        print("- 鼠标移动、点击、拖拽")
        print("- 键盘输入、特殊键、热键")
        print("- 滚动操作")
        print("\n✅ 可继续第3小时的屏幕捕捉学习")

        return 0

    except Exception as e:
        print(f"\n❌ 操作过程中出错: {e}")
        import traceback
        print(traceback.format_exc())
        return 1
    except KeyboardInterrupt:
        print("\n📴 用户中断")
        return 0


if __name__ == "__main__":
    sys.exit(main())
