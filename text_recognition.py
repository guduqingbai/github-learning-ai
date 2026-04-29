#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第6小时 - 文字识别练习脚本
演示如何使用Tesseract进行文字识别
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

    try:
        tesseract_version = pytesseract.get_tesseract_version()
        print(f"🎯 Tesseract版本: {tesseract_version}")
    except Exception as e:
        print(f"⚠️  Tesseract引擎不可用: {e}")
        print("📋 使用模拟模式")
        return False

    try:
        # 检查Tesseract配置
        import subprocess
        config = subprocess.check_output(['tesseract', '--list-langs'], text=True)
        print("📚 可用语言:")
        for lang in config.strip().split('\n'):
            if lang and not lang.startswith('List'):
                print(f"   - {lang}")
    except Exception as e:
        print(f"⚠️  无法检查语言列表: {e}")

    print()
    return True


def create_test_text_image():
    """创建包含文字的测试图像"""
    print("\n📝 创建文字测试图像")
    print("=" * 60)

    try:
        if os.path.exists("simple_text_test.png"):
            print("✅ 使用已存在的文字测试图像")
            return "simple_text_test.png"

        print("⚠️  无法直接捕捉文字区域，创建简单文字图像")

        height = 200
        width = 600
        img = np.zeros((height, width, 3), np.uint8)
        img.fill(255)

        cv2.putText(img, 'Test OCR', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        cv2.putText(img, 'Hello World!', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
        cv2.putText(img, '12345', (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)

        cv2.imwrite('simple_text_test.png', img)
        print(f"✅ 文字测试图像已创建: simple_text_test.png")
        print(f"🎯 图像尺寸: {width}x{height}")

        return "simple_text_test.png"

    except Exception as e:
        print(f"❌ 创建文字测试图像失败: {e}")
        import traceback
        print(traceback.format_exc())
        return None


def basic_text_recognition():
    """基础文字识别"""
    print("\n🎯 基础文字识别")
    print("=" * 60)

    try:
        text_image_file = create_test_text_image()
        if text_image_file is None:
            return False

        img = cv2.imread(text_image_file)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 二值化
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        cv2.imwrite("text_binary.png", binary)

        # 膨胀操作以增强文字
        kernel = np.ones((2, 2), np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=1)
        cv2.imwrite("text_dilated.png", dilated)

        # 测试多种预处理方法
        images_to_test = [
            ("原始图像", img),
            ("灰度图像", gray),
            ("二值化", binary),
            ("膨胀处理", dilated)
        ]

        print("🔍 不同预处理方法的识别结果:")

        best_result = None
        best_text = ""

        # 检查Tesseract是否可用
        tesseract_available = True
        try:
            # 尝试简单的调用
            from PIL import Image
            dummy_image = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))
            pytesseract.image_to_string(dummy_image)
        except Exception as e:
            print(f"⚠️  Tesseract OCR引擎未正确安装: {e}")
            tesseract_available = False

        if not tesseract_available:
            print("\n📋 Tesseract OCR 功能测试失败")
            print("🛠️  建议操作:")
            print("1. 下载并安装Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
            print("2. 确保将tesseract.exe添加到系统PATH")
            print("3. 安装语言包（如chi_sim.traineddata）到 tessdata 目录")
            return False

        for name, image in images_to_test:
            try:
                if len(image.shape) == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(image)

                text = pytesseract.image_to_string(pil_image, lang='eng')
                text = text.strip()

                print(f"\n🎯 {name}:")
                if text:
                    print(f"✅ 识别到文字:")
                    print(text)
                    if len(text) > len(best_text):
                        best_result = name
                        best_text = text
                else:
                    print("❌ 未识别到文字")

            except Exception as e:
                print(f"❌ {name}识别失败: {e}")

        if best_result:
            print(f"\n🎖️  最佳识别方法: {best_result}")

        return True

    except Exception as e:
        print(f"❌ 基础文字识别失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def advanced_recognition_options():
    """高级识别选项"""
    print("\n🚀 高级识别选项")
    print("=" * 60)

    try:
        if not os.path.exists("simple_text_test.png"):
            raise Exception("文字测试图像不存在")

        img = cv2.imread("simple_text_test.png")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 测试多种配置
        config_options = [
            ("默认配置", ""),
            ("白名单", "--psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
            ("黑名单", "--psm 6 -c tessedit_char_blacklist=!@#$%^&*()"),
            ("页码分割1", "--psm 6"),
            ("页码分割6", "--psm 11"),
            ("高分辨率", "--psm 12")
        ]

        print("📋 测试不同识别配置:")

        # 检查Tesseract是否可用
        tesseract_available = True
        try:
            from PIL import Image
            dummy_image = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))
            pytesseract.image_to_string(dummy_image)
        except Exception as e:
            print(f"⚠️  Tesseract OCR引擎未正确安装: {e}")
            tesseract_available = False

        if not tesseract_available:
            print("\n📋 Tesseract OCR 功能测试失败")
            print("🛠️  建议操作:")
            print("1. 下载并安装Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
            print("2. 确保将tesseract.exe添加到系统PATH")
            print("3. 安装语言包（如chi_sim.traineddata）到 tessdata 目录")
            return False

        for name, config in config_options:
            try:
                text = pytesseract.image_to_string(
                    gray,
                    config=config,
                    lang='eng'
                )
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


def performance_evaluation():
    """性能评估"""
    print("\n📊 识别性能评估")
    print("=" * 60)

    try:
        if not os.path.exists("simple_text_test.png"):
            raise Exception("文字测试图像不存在")

        img = cv2.imread("simple_text_test.png")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        methods = [
            ("直接识别", lambda: pytesseract.image_to_string(gray, lang='eng')),
            ("二值化", lambda: pytesseract.image_to_string(
                cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1],
                lang='eng'
            )),
            ("自适应阈值", lambda: pytesseract.image_to_string(
                cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 11, 2),
                lang='eng'
            )),
            ("开运算", lambda: pytesseract.image_to_string(
                cv2.morphologyEx(gray, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)),
                lang='eng'
            ))
        ]

        print("⏱️  识别时间测试:")

        # 检查Tesseract是否可用
        tesseract_available = True
        try:
            from PIL import Image
            dummy_image = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))
            pytesseract.image_to_string(dummy_image)
        except Exception as e:
            print(f"⚠️  Tesseract OCR引擎未正确安装: {e}")
            tesseract_available = False

        if not tesseract_available:
            print("\n📋 Tesseract OCR 功能测试失败")
            print("🛠️  建议操作:")
            print("1. 下载并安装Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
            print("2. 确保将tesseract.exe添加到系统PATH")
            print("3. 安装语言包（如chi_sim.traineddata）到 tessdata 目录")
            return False

        results = []
        for name, method in methods:
            start_time = time.time()

            # 多次识别以获取平均时间
            iterations = 3
            for _ in range(iterations):
                method()

            elapsed_time = (time.time() - start_time) / iterations
            results.append((name, elapsed_time))
            print(f"   - {name}: {elapsed_time * 1000:.1f} ms")

        # 找到最快的方法
        results.sort(key=lambda x: x[1])
        print(f"\n🚀 最快方法: {results[0][0]}")

        return True

    except Exception as e:
        print(f"❌ 性能评估失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def save_ocr_results():
    """保存OCR结果"""
    print("\n📄 保存识别结果")
    print("=" * 60)

    try:
        if not os.path.exists("simple_text_test.png"):
            raise Exception("文字测试图像不存在")

        img = cv2.imread("simple_text_test.png")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 检查Tesseract是否可用
        tesseract_available = True
        try:
            from PIL import Image
            dummy_image = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))
            pytesseract.image_to_string(dummy_image)
        except Exception as e:
            print(f"⚠️  Tesseract OCR引擎未正确安装: {e}")
            tesseract_available = False

        if not tesseract_available:
            print("\n📋 Tesseract OCR 功能测试失败")
            print("🛠️  建议操作:")
            print("1. 下载并安装Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
            print("2. 确保将tesseract.exe添加到系统PATH")
            print("3. 安装语言包（如chi_sim.traineddata）到 tessdata 目录")
            return False

        # 进行文字识别
        text = pytesseract.image_to_string(gray, lang='eng')
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
        show_tesseract_info()
        basic_text_recognition()
        advanced_recognition_options()
        performance_evaluation()
        save_ocr_results()

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
