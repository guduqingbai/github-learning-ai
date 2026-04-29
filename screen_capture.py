#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第3小时 - 屏幕捕捉练习脚本
演示如何使用Pillow进行屏幕捕捉
"""

import os
import time
import sys
from PIL import ImageGrab
import pyautogui


def create_output_dir():
    """创建输出目录"""
    output_dir = "captures"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 创建输出目录: {output_dir}")
    else:
        print(f"📁 使用现有目录: {output_dir}")
    return output_dir


def capture_full_screen(output_dir):
    """捕捉全屏"""
    print("\n📸 捕捉全屏")
    print("=" * 60)

    try:
        # 捕捉全屏
        print("🖥️  正在捕捉全屏...")
        screenshot = ImageGrab.grab()

        # 保存截图
        timestamp = int(time.time())
        filename = f"{output_dir}/full_screen_{timestamp}.png"
        screenshot.save(filename)
        print(f"✅ 全屏截图已保存: {filename}")

        # 获取图像信息
        width, height = screenshot.size
        print(f"📊 图像尺寸: {width}x{height}")
        print(f"🎨 图像模式: {screenshot.mode}")
        print(f"📦 文件大小: {os.path.getsize(filename) / 1024:.1f} KB")

        return filename

    except Exception as e:
        print(f"❌ 捕捉全屏失败: {e}")
        import traceback
        print(traceback.format_exc())
        return None


def capture_region(output_dir):
    """捕捉指定区域"""
    print("\n🎯 捕捉指定区域")
    print("=" * 60)

    try:
        # 选择一个区域 (从屏幕中心开始)
        center_x, center_y = pyautogui.size()
        center_x //= 2
        center_y //= 2

        region = (
            center_x - 200,
            center_y - 200,
            center_x + 200,
            center_y + 200
        )

        print(f"📏 捕捉区域: {region}")
        print("👀 移动鼠标到屏幕中心准备...")
        pyautogui.moveTo(center_x, center_y, duration=0.5)
        time.sleep(0.5)

        screenshot = ImageGrab.grab(bbox=region)

        timestamp = int(time.time())
        filename = f"{output_dir}/region_{timestamp}.png"
        screenshot.save(filename)
        print(f"✅ 区域截图已保存: {filename}")

        width, height = screenshot.size
        print(f"📊 区域尺寸: {width}x{height}")

        return filename

    except Exception as e:
        print(f"❌ 捕捉区域失败: {e}")
        import traceback
        print(traceback.format_exc())
        return None


def capture_multiple_regions(output_dir):
    """捕捉多个区域"""
    print("\n🎯 捕捉多个区域")
    print("=" * 60)

    regions = []
    center_x, center_y = pyautogui.size()
    center_x //= 2
    center_y //= 2

    # 创建四个象限的捕捉区域
    for i in range(4):
        offset_x = (-200 if i % 2 == 0 else 200)
        offset_y = (-200 if i < 2 else 200)
        region = (
            center_x + offset_x - 100,
            center_y + offset_y - 100,
            center_x + offset_x + 100,
            center_y + offset_y + 100
        )
        regions.append(region)

    captured_files = []

    for i, region in enumerate(regions, 1):
        try:
            print(f"📸 捕捉区域 {i}: {region}")
            screenshot = ImageGrab.grab(bbox=region)
            timestamp = int(time.time())
            filename = f"{output_dir}/quadrant_{i}_{timestamp}.png"
            screenshot.save(filename)
            captured_files.append(filename)
            print(f"✅ 区域 {i} 已保存: {filename}")
        except Exception as e:
            print(f"❌ 捕捉区域 {i} 失败: {e}")

    return captured_files


def display_capture_info(output_dir):
    """显示捕捉信息"""
    print("\n📊 捕捉信息统计")
    print("=" * 60)

    if not os.path.exists(output_dir):
        print("📁 输出目录不存在")
        return False

    files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
    if not files:
        print("📂 目录中没有PNG文件")
        return False

    total_size = 0
    for file in files:
        file_path = os.path.join(output_dir, file)
        total_size += os.path.getsize(file_path)

    print(f"📁 捕获文件数量: {len(files)}")
    print(f"📦 总文件大小: {total_size / 1024:.1f} KB")
    print(f"📂 目录路径: {os.path.abspath(output_dir)}")

    # 获取尺寸信息
    for file in sorted(files):
        try:
            with ImageGrab.open(os.path.join(output_dir, file)) as img:
                width, height = img.size
                mode = img.mode
                print(f"   - {file}: {width}x{height}, {mode}")
        except Exception as e:
            print(f"   - {file}: 无法读取")

    return True


def main():
    """主函数"""
    print("🚀 第3小时 - 屏幕捕捉练习")
    print("=" * 60)

    try:
        output_dir = create_output_dir()
        capture_full_screen(output_dir)
        capture_region(output_dir)
        capture_multiple_regions(output_dir)
        display_capture_info(output_dir)

        print("\n🎉 屏幕捕捉练习完成！")
        print("\n📋 已学习的操作:")
        print("- 全屏捕捉")
        print("- 指定区域捕捉")
        print("- 多区域捕捉")
        print("- 图像信息分析")
        print("- 截图管理")
        print("\n✅ 可继续第4小时的图像识别基础学习")

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
