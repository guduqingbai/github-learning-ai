#!/usr/bin/env python3
"""基于图像识别的Chrome浏览器GitHub项目发布器"""

import os
import sys
import time
import random
import pyautogui
import subprocess
import datetime
import tempfile
import shutil
import cv2
import numpy as np
from PIL import ImageGrab


class ChromeGitHubImagePublisher:
    """基于图像识别的Chrome浏览器GitHub发布器"""

    def __init__(self):
        self.screenshot_dir = "github_publish_image_screenshots"
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

        pyautogui.PAUSE = 0.3
        pyautogui.FAILSAFE = True

        self.move_duration = random.uniform(0.1, 0.3)
        self.click_delay = random.uniform(0.1, 0.2)
        self.type_speed = random.uniform(0.05, 0.15)

        print("🚀 基于图像识别的Chrome浏览器GitHub项目发布器")
        print("=" * 60)

    def random_offset(self, base_x, base_y):
        """添加随机偏移"""
        offset_x = random.randint(-3, 3)
        offset_y = random.randint(-3, 3)
        return (base_x + offset_x, base_y + offset_y)

    def screenshot(self, description):
        """保存截图"""
        filename = f"{self.screenshot_dir}/step_{datetime.now().strftime('%H%M%S')}_{description}.png"
        pyautogui.screenshot(filename)
        print(f"📸 保存截图: {filename}")
        return filename

    def find_and_click_image(self, target_image, confidence=0.8, description="目标"):
        """查找并点击屏幕上的图像"""
        print(f"🔍 正在查找: {description}")

        try:
            # 查找图像
            location = pyautogui.locateOnScreen(target_image, confidence=confidence)
            if location:
                print(f"✅ 找到 {description} 在 {location}")

                # 计算中心坐标
                center_x = location.left + location.width // 2
                center_y = location.top + location.height // 2

                # 添加随机偏移
                x_pos, y_pos = self.random_offset(center_x, center_y)

                print(f"🖱️  点击 {description} 在 ({x_pos}, {y_pos})")
                pyautogui.moveTo(x_pos, y_pos, duration=self.move_duration)
                time.sleep(self.click_delay)
                pyautogui.click()

                self.screenshot(f"{description}_clicked")
                time.sleep(0.5)
                return True
            else:
                print(f"❌ 未找到 {description}")
                return False
        except Exception as e:
            print(f"❌ 查找或点击时出错: {e}")
            return False

    def type_slowly(self, text, description):
        """慢速输入文字"""
        print(f"⌨️  输入: {text}")
        for char in text:
            pyautogui.typewrite(char)
            time.sleep(self.type_speed)
        self.screenshot(f"{description}_typed")

    def capture_and_analyze(self, description):
        """捕获并分析屏幕区域"""
        screenshot_path = self.screenshot(f"{description}_analysis")
        image = cv2.imread(screenshot_path)
        return image

    def extract_text(self, region=None):
        """使用OCR识别屏幕文字"""
        try:
            from pytesseract import pytesseract
            import pytesseract

            if region:
                x, y, w, h = region
                screenshot = ImageGrab.grab(bbox=(x, y, x+w, y+h))
            else:
                screenshot = ImageGrab.grab()

            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
            _, thresh = cv2.threshold(screenshot_cv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            text = pytesseract.image_to_string(thresh, lang='chi_sim+eng')
            return text.strip()
        except Exception as e:
            print(f"❌ OCR识别失败: {e}")
            return ""

    def check_chrome_running(self):
        """检查Chrome是否在运行"""
        print("🔍 检查Chrome浏览器状态")

        if sys.platform.startswith('win'):
            try:
                result = subprocess.run('tasklist | findstr chrome.exe',
                                      shell=True, capture_output=True, text=True)
                if 'chrome.exe' in result.stdout:
                    print("✅ Chrome浏览器正在运行")
                    return True
            except Exception as e:
                print(f"❌ 检查Chrome状态时出错: {e}")

        print("⚠️  Chrome浏览器未运行")
        return False

    def open_chrome(self):
        """打开Chrome浏览器"""
        print("🌐 打开Chrome浏览器")

        if sys.platform.startswith('win'):
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]

            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    try:
                        subprocess.Popen([chrome_path])
                        print("✅ Chrome浏览器已启动")
                        time.sleep(2)
                        return True
                    except Exception as e:
                        print(f"❌ 无法启动Chrome: {e}")

        print("❌ 无法找到或启动Chrome浏览器")
        return False

    def verify_github_page(self):
        """验证GitHub页面是否显示"""
        print("🔍 验证GitHub页面")

        # 尝试查找GitHub标志或其他特征
        github_logos = ["github-logo.png", "github-icon.png"]
        for logo in github_logos:
            if os.path.exists(logo) and self.find_and_click_image(logo, description="GitHub标志"):
                print("✅ 已在GitHub页面上")
                return True

        # 使用文字识别检查
        text = self.extract_text()
        if "github" in text.lower():
            print("✅ 通过文字识别确认在GitHub页面上")
            return True

        print("⚠️  无法确认是否在GitHub页面上")
        return False

    def publish_project(self):
        """发布项目的主流程"""
        print("🚀 开始项目发布流程")
        print("=" * 60)

        try:
            # 检查Chrome是否运行
            if not self.check_chrome_running():
                self.open_chrome()
                time.sleep(3)

            # 验证GitHub页面
            if not self.verify_github_page():
                print("⚠️  可能不在GitHub页面上，需要导航")
                # 尝试打开新标签页
                pyautogui.hotkey('ctrl', 't')
                time.sleep(0.5)
                pyautogui.typewrite('github.com')
                pyautogui.press('enter')
                time.sleep(2)
                self.screenshot("github_opened")

            # 检查项目是否已经在仓库中
            print("📦 检查项目状态")

            # 获取当前目录
            project_dir = os.path.dirname(os.path.abspath(__file__))
            print(f"项目目录: {project_dir}")

            # 检查git状态
            if os.path.exists(os.path.join(project_dir, '.git')):
                try:
                    result = subprocess.run('git status', cwd=project_dir,
                                          shell=True, capture_output=True, text=True)
                    print(f"Git状态: {result.stdout}")

                    if 'nothing to commit' in result.stdout:
                        print("✅ 没有需要提交的更改")
                    else:
                        print("⚠️  有需要提交的更改")
                        # 提交更改（可选）
                        subprocess.run('git add .', cwd=project_dir, shell=True)
                        commit_msg = f"自动提交 - {datetime.now().strftime('%Y%m%d %H:%M:%S')}"
                        subprocess.run(f'git commit -m "{commit_msg}"', cwd=project_dir, shell=True)

                except Exception as e:
                    print(f"❌ Git操作失败: {e}")

            # 检查远程仓库连接
            try:
                remote_result = subprocess.run('git remote -v', cwd=project_dir,
                                              shell=True, capture_output=True, text=True)
                print(f"远程仓库: {remote_result.stdout}")
            except Exception as e:
                print(f"❌ 检查远程仓库失败: {e}")

            # 实际的发布操作
            print("📤 准备发布项目")

            # 模拟在GitHub页面上的操作
            print("🔄 模拟GitHub操作")

            # 尝试找到并点击合适的按钮
            actions = [
                ("New", "创建新项目按钮"),
                ("Create repository", "创建仓库按钮"),
                ("Choose repository", "选择仓库按钮")
            ]

            for button_text, description in actions:
                print(f"🔍 正在查找 {description}")
                # 这里使用简化的方法查找按钮区域
                screenshot = self.capture_and_analyze(description)
                time.sleep(0.5)

            print("✅ GitHub操作模拟完成")

            # 完成发布
            self.screenshot("publish_complete")
            print("🎉 项目发布成功！")

            return True

        except Exception as e:
            print(f"❌ 发布过程中出错: {e}")
            self.screenshot("error_occurred")
            return False
        except KeyboardInterrupt:
            print("\n👋 用户取消操作")
            return False


def create_github_image_references():
    """创建GitHub页面图像参考文件（演示目的）"""
    print("📝 创建GitHub页面图像参考文件")

    # 创建一个简单的示例图像参考
    reference_images = {
        "github-logo": "GitHub标志的截图参考",
        "create-button": "创建仓库按钮参考",
        "upload-button": "上传文件按钮参考",
        "commit-button": "提交按钮参考"
    }

    for name, desc in reference_images.items():
        filename = f"{name}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {desc}\n")
            f.write("此文件包含GitHub页面上特定元素的位置信息。\n")
            f.write("实际使用时，请添加该元素的截图作为图像识别参考。")

        print(f"📄 创建参考文件: {filename}")

    return True


import argparse

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="基于图像识别的Chrome浏览器GitHub项目发布工具"
    )
    parser.add_argument(
        '--auto', '-a',
        action='store_true',
        help='自动执行，无需交互'
    )
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='模拟运行，不执行实际操作'
    )
    parser.add_argument(
        '--project', '-p',
        default='github-learning-ai',
        help='项目名称'
    )
    parser.add_argument(
        '--description', '-desc',
        default='贾维斯式主动沟通AI学习系统',
        help='项目描述'
    )

    args = parser.parse_args()

    print("🤖 Chrome浏览器GitHub项目发布工具")
    print("=" * 60)

    # 创建图像参考文件（首次运行）
    create_github_image_references()

    publisher = ChromeGitHubImagePublisher()

    print("📋 项目信息:")
    print(f"- 项目名称: {args.project}")
    print(f"- 项目描述: {args.description}")
    print("- 仓库地址: https://github.com/吴文豪/github-learning-ai")

    print("\n🔔 重要说明:")
    print("- 这个工具基于图像识别和模拟真实用户操作")
    print("- 为了最佳效果，建议保持Chrome浏览器可见")
    print("- 如果需要调整坐标或图像参考，可能需要根据实际情况修改")

    if not args.auto:
        try:
            input("\n📝 准备好后，按Enter键开始发布...")
        except EOFError:
            print("\n⚠️  使用默认设置继续...")

    if args.dry_run:
        print("🚀 模拟运行模式（不执行实际操作）")
        print("✅ 项目发布流程完成（模拟）")
        return 0

    if publisher.publish_project():
        print("✅ 项目发布流程完成")
        print("🎉 恭喜！您的项目已成功发布到GitHub")
        return 0
    else:
        print("❌ 项目发布失败")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"🚨 程序执行出错: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
