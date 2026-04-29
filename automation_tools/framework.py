#!/usr/bin/env python3
"""自动化框架主文件"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from image_recognition import ImageRecognition
from web_automation import WebAutomation


class AutomationFramework:
    """自动化框架"""

    def __init__(self):
        self.image_recognizer = ImageRecognition()
        self.web_automation = WebAutomation()

    def setup_github_automation(self):
        """设置GitHub自动化"""
        print("🎯 设置GitHub自动化")
        return self.web_automation.start_browser()

    def create_github_repo(self, repo_name, repo_desc):
        """创建GitHub仓库"""
        print(f"🚀 创建仓库: {repo_name}")
        return self.web_automation.create_github_repo(repo_name, repo_desc)

    def capture_and_recognize(self):
        """捕捉和识别屏幕"""
        print("📸 捕捉屏幕")
        text = self.image_recognizer.read_text()
        print(f"🎯 识别到文字: {text}")
        return text

    def run_complete_workflow(self):
        """运行完整工作流程"""
        print("🚀 启动完整自动化工作流程")
        print("="*60)

        if self.setup_github_automation():
            if self.create_github_repo("github-learning-ai", "贾维斯式主动沟通AI学习系统"):
                print("✅ GitHub仓库创建成功")

                text = self.capture_and_recognize()
                if text:
                    print("🎯 文字识别成功")

        return True
