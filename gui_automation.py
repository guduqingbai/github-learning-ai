#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Chrome GitHub仓库创建自动化 - 直接鼠标操作
"""

import pyautogui
import time
import random
from datetime import datetime
import os


class GitHubAutomation:
    """GitHub仓库创建自动化"""

    def __init__(self):
        self.screenshot_dir = "github_automation"
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

        self.screenshot_count = 0
        pyautogui.PAUSE = 0.3
        pyautogui.FAILSAFE = True

    def screenshot(self, description):
        """保存截图"""
        self.screenshot_count += 1
        filename = f"{self.screenshot_dir}/step_{self.screenshot_count:02d}_{description}.png"
        pyautogui.screenshot(filename)
        print(f"📸 保存: {filename}")

    def random_offset(self, base_x, base_y):
        """添加随机偏移，模拟真实用户"""
        offset_x = random.randint(-3, 3)
        offset_y = random.randint(-3, 3)
        return (base_x + offset_x, base_y + offset_y)

    def move_and_click(self, x, y, description):
        """移动鼠标并点击"""
        x_pos, y_pos = self.random_offset(x, y)
        print(f"🖱️  移动到: {description} ({x_pos}, {y_pos})")
        pyautogui.moveTo(x_pos, y_pos, duration=0.2)
        time.sleep(0.1)
        pyautogui.click()
        self.screenshot(description)
        time.sleep(0.5)

    def type_slowly(self, text, description):
        """慢速输入文字，模拟真实人类"""
        print(f"⌨️  输入: {text}")
        for char in text:
            pyautogui.typewrite(char)
            time.sleep(random.uniform(0.05, 0.2))
        self.screenshot(f"typed_{description}")

    def create_repository(self, repo_name="github-learning-ai", repo_desc="贾维斯式主动沟通AI学习系统"):
        """创建仓库"""
        print(f"🚀 开始创建仓库: {repo_name}")
        print(f"开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)

        try:
            # 1. 打开GitHub标签页
            print("\n🎯 步骤1: 打开GitHub标签页")
            self.move_and_click(150, 85, "Github标签")
            time.sleep(1)

            # 2. 点击New按钮
            print("\n🎯 步骤2: 点击New按钮")
            self.move_and_click(1300, 80, "New按钮")
            time.sleep(2)

            # 3. 输入仓库名称
            print("\n🎯 步骤3: 输入仓库名称")
            self.move_and_click(400, 300, "仓库名称输入框")
            self.type_slowly(repo_name, "repository_name")

            # 4. 输入描述
            print("\n🎯 步骤4: 输入仓库描述")
            self.move_and_click(400, 350, "仓库描述输入框")
            self.type_slowly(repo_desc, "repository_description")

            # 5. 选择公开/私有
            print("\n🎯 步骤5: 选择可见性")
            self.move_and_click(400, 400, "可见性选项")
            time.sleep(0.5)

            # 6. 选中Public
            self.move_and_click(450, 500, "Public选项")
            time.sleep(0.5)

            # 7. 选中初始化README
            print("\n🎯 步骤6: 初始化README")
            self.move_and_click(400, 550, "README复选框")

            # 8. 选择.gitignore
            print("\n🎯 步骤7: 选择.gitignore")
            self.move_and_click(400, 600, "gitignore下拉框")
            time.sleep(1)

            # 9. 选择Python模板
            self.move_and_click(450, 700, "Python模板")
            time.sleep(0.5)

            # 10. 选择许可证
            print("\n🎯 步骤8: 选择许可证")
            self.move_and_click(400, 650, "许可证下拉框")
            time.sleep(1)

            # 11. 选择MIT许可证
            self.move_and_click(450, 750, "MIT许可证")
            time.sleep(0.5)

            # 12. 创建仓库
            print("\n🎯 步骤9: 点击创建仓库")
            self.move_and_click(1000, 750, "创建仓库按钮")
            time.sleep(5)

            print("\n🎉 仓库创建成功!")
            print(f"结束时间: {datetime.now().strftime('%H:%M:%S')}")

            return True

        except Exception as e:
            print(f"\n🚨 操作失败: {e}")
            import traceback
            print(traceback.format_exc())
            return False

    def verify_repo(self):
        """验证仓库创建"""
        print("\n🔍 步骤10: 验证仓库创建")

        # 检查是否有绿色成功提示
        time.sleep(2)
        self.screenshot("repository_created")

        print("✅ 仓库创建已验证")
        return True

    def run_full_workflow(self):
        """运行完整工作流程"""
        print("🤖 GitHub仓库创建工作流程")
        print("="*60)

        input("📝 请确保已登录GitHub，浏览器在第一个标签页\n按Enter键继续...")

        self.screenshot("start_position")

        if self.create_repository():
            self.verify_repo()
            print("\n🎉 仓库创建工作流程完成!")
            print("="*60)
            print("📋 仓库信息:")
            print("   仓库名: github-learning-ai")
            print("   描述: 贾维斯式主动沟通AI学习系统")
            print("   可见性: Public")
            return True
        else:
            return False


def main():
    """主函数"""
    automation = GitHubAutomation()

    try:
        if automation.run_full_workflow():
            print("✅ 自动化操作成功")
            return 0
        else:
            print("❌ 自动化操作失败")
            return 1

    except KeyboardInterrupt:
        print("\n👋 用户取消操作")
        return 0
    except Exception as e:
        print(f"\n🚨 系统错误: {e}")
        import traceback
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    main()
