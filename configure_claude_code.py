#!/usr/bin/env python3
"""
⚙️ Claude Code配置管理工具
帮助用户配置Claude Code API密钥和其他设置
"""

import os
import sys
import json
import getpass
from pathlib import Path
from claude_code_adapter import ClaudeCodeAdapter


def configure_claude_code():
    """配置Claude Code"""
    print("⚙️  Claude Code配置管理")
    print("=" * 60)

    try:
        adapter = ClaudeCodeAdapter()

        print("📊 当前配置:")
        if adapter.is_available():
            print("   ✅ API密钥已配置")
        else:
            print("   ⚠️  API密钥未配置")
        print(f"   基础URL: {adapter.base_url}")
        print(f"   模型: {adapter.model}")
        print(f"   超时: {adapter.timeout}秒")
        print(f"   最大令牌: {adapter.max_tokens}")

        print("\n🎯 配置选项:")
        print("1. 设置API密钥")
        print("2. 修改基础URL")
        print("3. 更改模型")
        print("4. 调整超时时间")
        print("5. 修改最大令牌数")
        print("6. 显示配置文件内容")
        print("7. 重置为默认配置")
        print("8. 检查API连接")
        print("9. 退出")

        while True:
            choice = input("\n请选择操作 (1-9): ").strip()

            if choice == "1":
                api_key = getpass.getpass("请输入Claude Code API密钥: ").strip()
                if api_key:
                    adapter.update_config(api_key=api_key)
                    print("✅ API密钥已更新")
                else:
                    print("⚠️  API密钥不能为空")

            elif choice == "2":
                base_url = input("请输入API基础URL (默认: https://api.anthropic.com): ").strip()
                if base_url:
                    adapter.update_config(base_url=base_url)
                    print("✅ 基础URL已更新")
                else:
                    print("使用默认值")

            elif choice == "3":
                print("可用模型:")
                print("  - claude-3-sonnet-20250219 (默认)")
                print("  - claude-3-opus-20250219")
                print("  - claude-3-haiku-20250219")
                print("  - claude-2.1")

                model = input("请输入模型名称: ").strip()
                if model:
                    adapter.update_config(model=model)
                    print("✅ 模型已更新")

            elif choice == "4":
                try:
                    timeout = int(input("请输入超时时间 (秒, 默认: 60): ").strip())
                    adapter.update_config(timeout=timeout)
                    print("✅ 超时时间已更新")
                except ValueError:
                    print("⚠️  请输入有效的数字")

            elif choice == "5":
                try:
                    max_tokens = int(input("请输入最大令牌数 (默认: 4096): ").strip())
                    adapter.update_config(max_tokens=max_tokens)
                    print("✅ 最大令牌数已更新")
                except ValueError:
                    print("⚠️  请输入有效的数字")

            elif choice == "6":
                config_file = Path("data") / "claude_code_config.json"
                if config_file.exists():
                    with open(config_file, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                    print("配置文件内容:")
                    print(json.dumps(config_data, ensure_ascii=False, indent=2))
                else:
                    print("配置文件不存在")

            elif choice == "7":
                confirm = input("确定要重置为默认配置吗? (y/N): ").lower().strip()
                if confirm == "y":
                    adapter.update_config(
                        api_key="",
                        base_url="https://api.anthropic.com",
                        model="claude-3-sonnet-20250219",
                        timeout=60,
                        max_tokens=4096
                    )
                    print("✅ 配置已重置为默认值")

            elif choice == "8":
                print("正在检查API连接...")
                if adapter.is_available():
                    # 尝试一个简单的API调用
                    test_response = adapter.create_code_suggestions("创建一个简单的Hello World程序", "Python")
                    if test_response:
                        print("✅ API连接正常")
                    else:
                        print("⚠️  API连接测试失败")
                else:
                    print("⚠️  请先配置API密钥")

            elif choice == "9":
                print("✅ 配置完成")
                break

            else:
                print("⚠️  无效的选择，请输入1-9")

    except KeyboardInterrupt:
        print("\n\n✅ 配置工具已退出")
    except Exception as e:
        print(f"\n❌ 配置过程出错: {e}")
        import traceback
        print(traceback.format_exc())


def quick_configure():
    """快速配置模式"""
    print("⚡ 快速配置模式")
    print("=" * 60)

    try:
        adapter = ClaudeCodeAdapter()

        print("📝 快速配置API密钥")
        api_key = input("请输入Claude Code API密钥: ").strip()

        if api_key:
            adapter.update_config(api_key=api_key)
            print("✅ API密钥已设置")

            print("\n🔍 检查API连接...")
            test_response = adapter.create_code_suggestions("创建一个简单的Hello World程序", "Python")
            if test_response:
                print("✅ API连接正常")
                print("🎉 Claude Code配置完成!")
            else:
                print("⚠️  API连接测试失败")
        else:
            print("⚠️  API密钥不能为空")

    except Exception as e:
        print(f"\n❌ 配置失败: {e}")
        import traceback
        print(traceback.format_exc())


def show_environment_info():
    """显示环境信息"""
    print("🌍 系统环境信息")
    print("=" * 60)

    print("Python版本:", sys.version)
    print("操作系统:", sys.platform)

    config_file = Path("data") / "claude_code_config.json"
    if config_file.exists():
        print("配置文件位置:", config_file.resolve())

    data_dir = Path("data")
    if data_dir.exists():
        print("数据目录:", data_dir.resolve())
    else:
        print("数据目录不存在，将自动创建")


def main():
    """主函数"""
    print("🚀 Claude Code配置管理工具")
    print("=" * 60)

    show_environment_info()

    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_configure()
    else:
        print("\n可用命令:")
        print("  python configure_claude_code.py")
        print("  python configure_claude_code.py quick")

        configure_claude_code()


if __name__ == "__main__":
    main()
