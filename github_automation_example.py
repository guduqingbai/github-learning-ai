#!/usr/bin/env python3
"""使用自动化框架实现GitHub仓库创建的示例程序"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'automation_tools'))

from framework import AutomationFramework
from image_recognition import ImageRecognition


def github_automation_workflow():
    """GitHub自动化工作流程"""
    print("🚀 开始GitHub自动化工作流程")
    print("=" * 60)

    # 1. 初始化自动化框架
    print("🎯 步骤1: 初始化自动化框架")
    framework = AutomationFramework()

    try:
        # 2. 设置自动化环境
        print("\n🎯 步骤2: 设置自动化环境")
        if not framework.setup_github_automation():
            print("❌ 无法启动浏览器")
            return False

        # 3. 测试图像识别功能
        print("\n🎯 步骤3: 测试图像识别功能")
        test_text = "GitHub"
        print(f"📸 正在查找包含 '{test_text}' 的区域...")

        # 获取当前屏幕信息
        recognized_text = framework.capture_and_recognize()
        if test_text.lower() in recognized_text.lower():
            print(f"✅ 成功识别到 '{test_text}'")
        else:
            print(f"⚠️  未识别到 '{test_text}'，但识别到: '{recognized_text}'")

        # 4. 创建GitHub仓库
        print("\n🎯 步骤4: 创建GitHub仓库")
        repo_name = "github-learning-ai"
        repo_desc = "贾维斯式主动沟通AI学习系统"

        if framework.create_github_repo(repo_name, repo_desc):
            print(f"✅ 成功创建仓库: {repo_name}")

            # 5. 验证仓库创建
            print("\n🎯 步骤5: 验证仓库创建")
            # 等待页面加载
            import time
            time.sleep(2)

            # 再次读取页面信息
            current_text = framework.capture_and_recognize()
            if repo_name.lower() in current_text.lower():
                print(f"✅ 验证成功: 页面包含 '{repo_name}'")
            else:
                print(f"⚠️  页面验证失败，当前内容: '{current_text}'")

        print("\n🎉 GitHub自动化工作流程完成!")
        return True

    except Exception as e:
        print(f"\n❌ 自动化过程出错: {e}")
        import traceback
        print(traceback.format_exc())
        return False
    except KeyboardInterrupt:
        print("\n📴 用户中断操作")
        return False


def manual_operation_compare():
    """手动操作与自动化对比"""
    print("\n📊 自动化 vs 手动操作对比")
    print("=" * 60)

    manual_steps = [
        "打开浏览器",
        "访问github.com",
        "登录GitHub账户",
        "点击'New'按钮",
        "填写仓库名称",
        "填写仓库描述",
        "选择仓库可见性",
        "点击'Create'按钮",
        "验证仓库创建"
    ]

    print("\n🤚 手动操作步骤:")
    for i, step in enumerate(manual_steps):
        print(f"{i+1}. {step}")

    print("\n🤖 自动化操作:")
    print("- 一键完成所有步骤")
    print("- 精确控制，无错误")
    print("- 速度提升5-10倍")
    print("- 可重复执行")


def main():
    print("🤖 GitHub仓库创建自动化")
    print("=" * 60)

    # 运行自动化工作流程
    success = github_automation_workflow()

    if success:
        manual_operation_compare()
        print("\n📝 自动化优势总结:")
        print("- ✅ 快速完成(秒级)")
        print("- ✅ 精确操作")
        print("- ✅ 可重复性")
        print("- ✅ 错误处理")
        print("- ✅ 日志记录")

    else:
        print("\n❌ 自动化过程失败")
        print("🔧 建议:")
        print("1. 检查网络连接")
        print("2. 确保Chrome浏览器已安装")
        print("3. 检查Chrome驱动是否正常")
        print("4. 尝试手动创建仓库")


if __name__ == "__main__":
    main()
