#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第5小时 - 模板匹配练习脚本
演示如何使用OpenCV进行模板匹配
"""

import os
import time
import sys
import cv2
import numpy as np
from PIL import ImageGrab
import pyautogui


def show_template_matching_intro():
    """介绍模板匹配"""
    print("🎯 模板匹配介绍")
    print("=" * 60)

    info = [
        "📋 什么是模板匹配?",
        "- 在图像中寻找与指定模板相似的区域",
        "- 计算图像与模板的匹配度",
        "- 返回最佳匹配位置",
        "",
        "🚀 常用的匹配方法:",
        "- cv2.TM_CCOEFF: 相关系数匹配",
        "- cv2.TM_CCOEFF_NORMED: 归一化相关系数匹配",
        "- cv2.TM_CCORR: 相关匹配",
        "- cv2.TM_CCORR_NORMED: 归一化相关匹配",
        "- cv2.TM_SQDIFF: 平方差匹配",
        "- cv2.TM_SQDIFF_NORMED: 归一化平方差匹配",
        "",
        "🎯 匹配方法特点:",
        "- TM_SQDIFF: 值越小匹配度越高",
        "- 其他方法: 值越大匹配度越高",
        "- 归一化方法对光照变化更鲁棒"
    ]

    for line in info:
        print(line)

    time.sleep(3)


def create_test_template():
    """创建测试模板"""
    print("\n📐 创建测试模板")
    print("=" * 60)

    try:
        # 确保有样本图像
        if not os.path.exists("sample_original.png"):
            print("📸 捕获新的样本图像")
            sample_image = ImageGrab.grab(bbox=(1000, 500, 1200, 700))
            sample_image_cv = cv2.cvtColor(np.array(sample_image), cv2.COLOR_RGB2BGR)
            cv2.imwrite("sample_original.png", sample_image_cv)
            print("✅ 新样本图像已创建")

        # 加载图像
        img = cv2.imread("sample_original.png")
        if img is None:
            raise Exception("无法加载样本图像")

        # 选择图像中一个小区域作为模板
        h, w = img.shape[:2]
        template = img[int(h/4):int(h*3/4), int(w/4):int(w*3/4)]
        cv2.imwrite("test_template.png", template)
        print(f"✅ 测试模板已创建: test_template.png")
        print(f"🎯 模板尺寸: {template.shape[1]}x{template.shape[0]}")

        return "test_template.png"

    except Exception as e:
        print(f"❌ 创建测试模板失败: {e}")
        import traceback
        print(traceback.format_exc())
        return None


def single_template_match():
    """单一模板匹配"""
    print("\n🎯 单一模板匹配")
    print("=" * 60)

    try:
        template_file = create_test_template()
        if template_file is None:
            return False

        img = cv2.imread("sample_original.png")
        template = cv2.imread(template_file)

        w, h = template.shape[:2]

        # 测试多种匹配方法
        methods = [
            (cv2.TM_CCOEFF, "TM_CCOEFF"),
            (cv2.TM_CCOEFF_NORMED, "TM_CCOEFF_NORMED"),
            (cv2.TM_CCORR, "TM_CCORR"),
            (cv2.TM_CCORR_NORMED, "TM_CCORR_NORMED"),
            (cv2.TM_SQDIFF, "TM_SQDIFF"),
            (cv2.TM_SQDIFF_NORMED, "TM_SQDIFF_NORMED")
        ]

        best_match = None
        best_loc = None
        best_val = None

        for method, method_name in methods:
            # 应用模板匹配
            res = cv2.matchTemplate(img, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            # 确定最佳匹配位置
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
                match_val = min_val
            else:
                top_left = max_loc
                match_val = max_val

            bottom_right = (top_left[0] + w, top_left[1] + h)

            print(f"🔍 {method_name}:")
            print(f"   - 匹配值: {match_val:.3f}")
            print(f"   - 位置: {top_left} -> {bottom_right}")

            # 保存结果图像
            img_copy = img.copy()
            cv2.rectangle(img_copy, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(img_copy, method_name, (top_left[0], top_left[1]-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.imwrite(f"match_result_{method_name}.png", img_copy)

            # 跟踪最佳匹配
            if method == cv2.TM_CCOEFF_NORMED:
                best_match = method_name
                best_loc = top_left
                best_val = match_val

        print(f"\n🎖️  最佳匹配方法: {best_match}")
        print(f"   值: {best_val:.3f}")
        print(f"   位置: {best_loc}")

        return True

    except Exception as e:
        print(f"❌ 单一模板匹配失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def multiple_template_matching():
    """多模板匹配"""
    print("\n🎯 多模板匹配")
    print("=" * 60)

    try:
        # 在测试图像中寻找多个可能的匹配
        img = cv2.imread("sample_original.png")
        template = cv2.imread("test_template.png")

        if img is None or template is None:
            raise Exception("无法加载图像或模板")

        w, h = template.shape[:2]

        # 使用归一化相关系数匹配方法
        method = cv2.TM_CCOEFF_NORMED
        res = cv2.matchTemplate(img, template, method)

        # 设置匹配阈值
        threshold = 0.8
        locations = np.where(res >= threshold)

        print(f"🎯 匹配阈值: {threshold}")
        print(f"📊 找到 {len(locations[0])} 个匹配")

        if len(locations[0]) > 0:
            img_copy = img.copy()
            for pt in zip(*locations[::-1]):
                bottom_right = (pt[0] + w, pt[1] + h)
                cv2.rectangle(img_copy, pt, bottom_right, (0, 0, 255), 2)
                cv2.putText(img_copy, f"{res[pt[1]][pt[0]]:.2f}", (pt[0], pt[1]-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            cv2.imwrite("multiple_matches.png", img_copy)
            print(f"✅ 多匹配结果已保存: multiple_matches.png")

            # 统计匹配质量
            match_values = []
            for y, x in zip(locations[0], locations[1]):
                match_values.append(res[y, x])

            avg_match = np.mean(match_values)
            max_match = np.max(match_values)
            print(f"📊 匹配值统计:")
            print(f"   - 平均: {avg_match:.3f}")
            print(f"   - 最高: {max_match:.3f}")
            print(f"   - 范围: {min(match_values):.3f} - {max(match_values):.3f}")

        else:
            print("⚠️  没有找到满足阈值的匹配")

        return True

    except Exception as e:
        print(f"❌ 多模板匹配失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def performance_evaluation():
    """性能评估"""
    print("\n📊 性能评估")
    print("=" * 60)

    try:
        img = cv2.imread("sample_original.png")
        template = cv2.imread("test_template.png")

        methods = [
            (cv2.TM_CCOEFF, "TM_CCOEFF"),
            (cv2.TM_CCOEFF_NORMED, "TM_CCOEFF_NORMED"),
            (cv2.TM_CCORR, "TM_CCORR"),
            (cv2.TM_CCORR_NORMED, "TM_CCORR_NORMED"),
            (cv2.TM_SQDIFF, "TM_SQDIFF"),
            (cv2.TM_SQDIFF_NORMED, "TM_SQDIFF_NORMED")
        ]

        print("⏱️  匹配时间测试:")

        results = []
        for method, method_name in methods:
            start_time = time.time()

            # 执行多次匹配以获取平均时间
            iterations = 10
            for _ in range(iterations):
                cv2.matchTemplate(img, template, method)

            elapsed_time = (time.time() - start_time) / iterations
            results.append((method_name, elapsed_time))

            print(f"   - {method_name}: {elapsed_time * 1000:.1f} ms")

        # 找到最快和最慢的方法
        results.sort(key=lambda x: x[1])
        print(f"\n🚀 最快方法: {results[0][0]}")
        print(f"🐢 最慢方法: {results[-1][0]}")

        return True

    except Exception as e:
        print(f"❌ 性能评估失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def main():
    """主函数"""
    print("🚀 第5小时 - 模板匹配练习")
    print("=" * 60)

    try:
        show_template_matching_intro()
        single_template_match()
        multiple_template_matching()
        performance_evaluation()

        print("\n🎉 模板匹配练习完成！")
        print("\n📋 已学习的操作:")
        print("- 模板创建和提取")
        print("- 6种不同匹配方法")
        print("- 归一化匹配值解释")
        print("- 多模板匹配")
        print("- 性能评估")
        print("- 匹配结果可视化")
        print("\n✅ 可继续第6小时的文字识别学习")

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
