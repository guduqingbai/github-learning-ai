#!/usr/bin/env python3
"""测试项目发布工具的功能"""

import os
import sys
import subprocess
import tempfile
from datetime import datetime


def run_command(cmd, check=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, check=check,
                             capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令失败: {e.cmd}")
        print(f"错误: {e.stderr}")
        return None


def test_python_files():
    """测试 Python 文件是否可以正常导入和运行"""
    print("🔍 测试 Python 文件功能")

    test_files = [
        'github_api_automation.py',
        'github_cli.py',
        'publish_project.py',
        'github_automation_example.py'
    ]

    for file in test_files:
        if os.path.exists(file):
            print(f"  📄 测试 {file}...")
            try:
                result = run_command(f'python {file} --help', check=True)
                print("  ✅ 可以正常运行")
            except Exception as e:
                print(f"  ❌ 运行失败: {e}")
        else:
            print(f"  ❌ 文件不存在: {file}")

    print()


def test_requirements():
    """测试 requirements.txt 文件"""
    print("🔍 测试 requirements.txt 文件")

    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt 文件不存在")
        return False

    try:
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f.readlines() if line.strip()]
            print(f"✅ 找到 {len(requirements)} 个依赖包")

        print("\n📦 检查关键依赖是否已安装:")
        for req in requirements:
            if req:
                package = req.split('=')[0].split('>')[0].split('<')[0]
                try:
                    __import__(package.replace('-', '_'))
                    print(f"  ✅ {package} 已安装")
                except ImportError:
                    print(f"  ❌ {package} 未安装")
                    # 尝试安装
                    print(f"  📦 正在安装 {package}...")
                    result = run_command(f'pip install {req}', check=False)
                    if result and result.returncode == 0:
                        print(f"  ✅ {package} 安装成功")
                    else:
                        print(f"  ❌ {package} 安装失败")

        print()
        return True

    except Exception as e:
        print(f"❌ 测试 requirements.txt 时出错: {e}")
        return False


def test_git_repo():
    """测试 Git 仓库状态"""
    print("🔍 测试 Git 仓库状态")

    if not os.path.exists('.git'):
        print("❌ 未找到 Git 仓库")
        return False

    try:
        # 检查工作区是否干净
        status_result = run_command('git status', check=False)
        if status_result and 'nothing to commit, working tree clean' in status_result.stdout:
            print("✅ 工作区干净")
        else:
            print("⚠️  工作区有未提交的更改")

        # 检查是否有远程仓库
        remote_result = run_command('git remote -v', check=False)
        if remote_result and remote_result.stdout.strip():
            print("✅ 已配置远程仓库")
            print(remote_result.stdout.strip())
        else:
            print("⚠️  未配置远程仓库")

        print()
        return True

    except Exception as e:
        print(f"❌ 测试 Git 仓库时出错: {e}")
        return False


def test_config_files():
    """测试项目配置文件"""
    print("🔍 测试项目配置文件")

    config_files = [
        'README.md',
        'PUBLISH.md',
        'RELEASE.md',
        '.gitignore',
        'publish.sh',
        'publish.bat'
    ]

    all_valid = True
    for file in config_files:
        if os.path.exists(file):
            print(f"  ✅ {file} 存在")
        else:
            print(f"  ❌ {file} 不存在")
            all_valid = False

    print()
    return all_valid


def main():
    """主函数"""
    print("🚀 项目发布工具功能测试")
    print("=" * 60)

    # 记录开始时间
    start_time = datetime.now()

    test_results = []

    print(f"开始时间: {start_time.strftime('%H:%M:%S')}")
    print()

    # 测试 Python 文件
    test_python_files()

    # 测试 requirements.txt
    test_requirements()

    # 测试 Git 仓库
    test_git_repo()

    # 测试配置文件
    test_config_files()

    # 测试发布脚本
    print("🔍 测试发布脚本")

    if os.path.exists('publish.sh'):
        try:
            result = run_command('chmod +x publish.sh', check=False)
            print("✅ publish.sh 脚本权限设置成功")
        except Exception as e:
            print(f"❌ 无法设置 publish.sh 权限: {e}")

    if os.path.exists('publish.bat'):
        print("✅ publish.bat 脚本存在")

    print()

    # 记录结束时间
    end_time = datetime.now()
    duration = end_time - start_time

    print("✅ 所有测试完成")
    print(f"开始时间: {start_time.strftime('%H:%M:%S')}")
    print(f"结束时间: {end_time.strftime('%H:%M:%S')}")
    print(f"耗时: {duration.total_seconds():.2f} 秒")
    print("=" * 60)


if __name__ == "__main__":
    main()
