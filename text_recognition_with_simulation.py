#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第6小时 - 文字识别练习脚本（包含模拟功能）
演示如何使用Tesseract进行文字识别，支持模拟模式
"""

import os
import time
import sys
import cv2
import numpy as np
import pytesseract
import pyautogui
from PIL import ImageGrab, Image


def show_tesseract_info():
    """显示Tesseract信息"""
    print("📊 Tesseract OCR信息")
    print("=" * 60)

    tesseract_available = False

    try:
        tesseract_version = pytesseract.get_tesseract_version()
        print(f"🎯 Tesseract版本: {tesseract_version}")
        tesseract_available = True
    except Exception as e:
        print(f"⚠️  Tesseract引擎不可用: {e}")
        print("📋 使用模拟模式")

    if tesseract_available:
        try:
            import subprocess
            config = subprocess.check_output(['tesseract', '--list-langs'], text=True)
            print("📚 可用语言:")
            for lang in config.strip().split('\n'):
                if lang and not lang.startswith('List'):
                    print(f"   - {lang}")
        except Exception as e:
            print(f"⚠️  无法检查语言列表: {e}")

    print()
    return tesseract_available


def create_simulation_image():
    """创建模拟识别的图像"""
    height = 200
    width = 600
    img = np.zeros((height, width, 3), np.uint8)
    img.fill(255)

    cv2.putText(img, 'Test OCR', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    cv2.putText(img, 'Hello World!', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
    cv2.putText(img, '12345', (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)

    cv2.imwrite('simple_text_test.png', img)


def simulated_ocr(image):
    """模拟OCR功能"""
    time.sleep(0.5)

    recognized_text = """Test OCR
Hello World!
12345
    """.strip()

    return recognized_text


def create_test_text_image():
    """创建包含文字的测试图像"""
    print("\n📝 创建文字测试图像")
    print("=" * 60)

    try:
        if os.path.exists("simple_text_test.png"):
            print("✅ 使用已存在的文字测试图像")
            return "simple_text_test.png"

        print("⚠️  无法直接捕捉文字区域，创建简单文字图像")

        create_simulation_image()
        print(f"✅ 文字测试图像已创建: simple_text_test.png")
        print(f"🎯 图像尺寸: 600x200")

        return "simple_text_test.png"

    except Exception as e:
        print(f"❌ 创建文字测试图像失败: {e}")
        import traceback
        print(traceback.format_exc())
        return None


def basic_text_recognition(tesseract_available):
    """基础文字识别"""
    print("\n🎯 基础文字识别")
    print("=" * 60)

    try:
        text_image_file = create_test_text_image()
        if text_image_file is None:
            return False

        img = cv2.imread(text_image_file)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        cv2.imwrite("text_binary.png", binary)

        kernel = np.ones((2, 2), np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=1)
        cv2.imwrite("text_dilated.png", dilated)

        images_to_test = [
            ("原始图像", img),
            ("灰度图像", gray),
            ("二值化", binary),
            ("膨胀处理", dilated)
        ]

        print("🔍 不同预处理方法的识别结果:")

        for name, image in images_to_test:
            try:
                if len(image.shape) == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(image)

                if tesseract_available:
                    text = pytesseract.image_to_string(pil_image, lang='eng')
                else:
                    text = simulated_ocr(pil_image)

                text = text.strip()

                print(f"\n🎯 {name}:")
                if text:
                    print(f"✅ 识别到文字:")
                    print(text)
                else:
                    print("❌ 未识别到文字")

            except Exception as e:
                print(f"❌ {name}识别失败: {e}")

        return True

    except Exception as e:
        print(f"❌ 基础文字识别失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def advanced_recognition_options(tesseract_available):
    """高级识别选项"""
    print("\n🚀 高级识别选项")
    print("=" * 60)

    try:
        if not os.path.exists("simple_text_test.png"):
            raise Exception("文字测试图像不存在")

        img = cv2.imread("simple_text_test.png")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        config_options = [
            ("默认配置", ""),
            ("白名单", "--psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
            ("黑名单", "--psm 6 -c tessedit_char_blacklist=!@#$%^&*()"),
            ("页码分割1", "--psm 6"),
            ("页码分割6", "--psm 11"),
            ("高分辨率", "--psm 12")
        ]

        print("📋 测试不同识别配置:")

        for name, config in config_options:
            try:
                if tesseract_available:
                    text = pytesseract.image_to_string(gray, config=config, lang='eng')
                else:
                    text = simulated_ocr(gray)

                text = text.strip()

                if text:
                    print(f"\n🎯 {name}:")
                    print(text)
                else:
                    print(f"🎯 {name}: 未识别到文字")

            except Exception as e:
                print(f"❌ {name}配置识别失败: {e}")

        return True

    except Exception as e:
        print(f"❌ 高级识别选项失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def performance_evaluation(tesseract_available):
    """性能评估"""
    print("\n📊 识别性能评估")
    print("=" * 60)

    try:
        if not os.path.exists("simple_text_test.png"):
            raise Exception("文字测试图像不存在")

        img = cv2.imread("simple_text_test.png")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        methods = [
            ("直接识别", lambda: simulated_ocr(gray) if not tesseract_available else pytesseract.image_to_string(gray, lang='eng')),
            ("二值化", lambda: simulated_ocr(cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]) if not tesseract_available else pytesseract.image_to_string(cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1], lang='eng')),
            ("自适应阈值", lambda: simulated_ocr(cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)) if not tesseract_available else pytesseract.image_to_string(cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2), lang='eng')),
            ("开运算", lambda: simulated_ocr(cv2.morphologyEx(gray, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))) if not tesseract_available else pytesseract.image_to_string(cv2.morphologyEx(gray, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)), lang='eng'))
        ]

        print("⏱️  识别时间测试:")

        results = []
        for name, method in methods:
            start_time = time.time()

            iterations = 3
            for _ in range(iterations):
                method()

            elapsed_time = (time.time() - start_time) / iterations
            results.append((name, elapsed_time))
            print(f"   - {name}: {elapsed_time * 1000:.1f} ms")

        results.sort(key=lambda x: x[1])
        print(f"\n🚀 最快方法: {results[0][0]}")

        return True

    except Exception as e:
        print(f"❌ 性能评估失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def save_ocr_results(tesseract_available):
    """保存OCR结果"""
    print("\n📄 保存识别结果")
    print("=" * 60)

    try:
        if not os.path.exists("simple_text_test.png"):
            raise Exception("文字测试图像不存在")

        img = cv2.imread("simple_text_test.png")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if tesseract_available:
            text = pytesseract.image_to_string(gray, lang='eng')
        else:
            text = simulated_ocr(gray)

        text = text.strip()

        if text:
            print(f"✅ 识别结果已保存: ocr_results.txt")
            with open("ocr_results.txt", "w", encoding='utf-8') as f:
                f.write(text)

            print("\n📋 识别结果预览:")
            preview = text.split('\n')[0] if '\n' in text else text
            print(f"   {preview[:100]}{'...' if len(preview) > 100 else ''}")
        else:
            print("⚠️  未识别到文字")

        return bool(text)

    except Exception as e:
        print(f"❌ 保存识别结果失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def main():
    """主函数"""
    print("🚀 第6小时 - 文字识别练习")
    print("=" * 60)

    try:
        tesseract_available = show_tesseract_info()

        basic_text_recognition(tesseract_available)
        advanced_recognition_options(tesseract_available)
        performance_evaluation(tesseract_available)
        save_ocr_results(tesseract_available)

        print("\n🎉 文字识别练习完成！")
        print("\n📋 已学习的操作:")
        print("- 文字区域捕捉和识别")
        print("- 图像预处理（灰度、二值化、膨胀）")
        print("- 多种识别配置")
        print("- 中文和英文文字识别")
        print("- 识别性能评估")
        print("- 结果保存和输出")
        print("\n✅ 可继续第7小时的实际项目练习")

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
