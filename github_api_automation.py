#!/usr/bin/env python3
"""GitHub API 自动化脚本 - 完全命令行操作，无需手动干预"""

import requests
import json
import subprocess
import os
import sys
import argparse
from datetime import datetime


class GitHubAPIAutomation:
    """GitHub API 自动化类"""

    def __init__(self, token=None):
        self.token = token or os.environ.get('GITHUB_TOKEN')
        if not self.token:
            raise Exception("GitHub token not provided and not found in GITHUB_TOKEN environment variable")

        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def create_repository(self, repo_name, repo_desc="", private=False):
        """使用 GitHub API 创建仓库"""
        print(f"🚀 创建仓库: {repo_name}")

        url = 'https://api.github.com/user/repos'
        data = {
            'name': repo_name,
            'description': repo_desc,
            'private': private,
            'auto_init': True,
            'gitignore_template': 'Python',
            'license_template': 'mit'
        }

        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))

            if response.status_code == 201:
                print(f"✅ 仓库创建成功: {repo_name}")
                repo_data = response.json()
                return repo_data['html_url'], repo_data['ssh_url'], repo_data['clone_url']
            else:
                print(f"❌ 仓库创建失败 (HTTP {response.status_code}): {response.text}")
                return None
        except Exception as e:
            print(f"❌ 创建仓库时出错: {e}")
            return None

    def check_repository_exists(self, repo_name):
        """检查仓库是否存在"""
        print(f"🔍 检查仓库是否存在: {repo_name}")

        url = f'https://api.github.com/repos/{self.get_username()}/{repo_name}'

        try:
            response = requests.get(url, headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ 检查仓库存在性时出错: {e}")
            return False

    def get_username(self):
        """获取当前认证用户的用户名"""
        try:
            response = requests.get('https://api.github.com/user', headers=self.headers)
            if response.status_code == 200:
                return response.json()['login']
        except Exception as e:
            print(f"❌ 获取用户名时出错: {e}")
        return None

    def initialize_and_push_repo(self, repo_dir, repo_name, repo_url, remote_name='origin'):
        """初始化本地仓库并推送到远程"""
        print(f"📦 初始化并推送仓库: {repo_name}")

        try:
            # 进入项目目录
            original_dir = os.getcwd()
            os.chdir(repo_dir)

            # 初始化 Git 仓库
            subprocess.run(['git', 'init'], check=True, capture_output=True, text=True)

            # 配置 Git
            subprocess.run(['git', 'config', 'user.name', 'GitHub Automation'], check=True, capture_output=True, text=True)
            subprocess.run(['git', 'config', 'user.email', 'automation@example.com'], check=True, capture_output=True, text=True)

            # 添加远程仓库
            subprocess.run(['git', 'remote', 'add', remote_name, repo_url], check=True, capture_output=True, text=True)

            # 添加所有文件
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True, text=True)

            # 提交
            commit_msg = f"Initial commit - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True, text=True)

            # 推送
            subprocess.run(['git', 'push', '-u', remote_name, 'main'], check=True, capture_output=True, text=True)

            print(f"✅ 成功推送到远程仓库: {repo_url}")

            os.chdir(original_dir)
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Git 操作失败: {e.stderr}")
            os.chdir(original_dir)
            return False
        except Exception as e:
            print(f"❌ 初始化和推送仓库时出错: {e}")
            os.chdir(original_dir)
            return False


def setup_git_credentials():
    """设置 Git 凭证助手"""
    try:
        print("🔑 配置 Git 凭证助手")
        subprocess.run(['git', 'config', '--global', 'credential.helper', 'store'], check=True)
        return True
    except Exception as e:
        print(f"❌ 配置 Git 凭证助手时出错: {e}")
        return False


def install_requirements(requirements_file='requirements.txt'):
    """安装项目依赖"""
    if not os.path.exists(requirements_file):
        print("⚠️  requirements.txt 文件不存在，跳过依赖安装")
        return True

    try:
        print("📦 安装项目依赖")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file],
                     check=True, capture_output=True, text=True)
        print("✅ 依赖安装完成")
        return True
    except Exception as e:
        print(f"❌ 安装依赖时出错: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="GitHub API 自动化工具"
    )

    parser.add_argument(
        '--token', '-t',
        help="GitHub 个人访问令牌 (PAT)"
    )
    parser.add_argument(
        '--repo', '-r',
        default="github-learning-ai",
        help="GitHub 仓库名称"
    )
    parser.add_argument(
        '--desc', '-d',
        default="贾维斯式主动沟通AI学习系统",
        help="仓库描述"
    )
    parser.add_argument(
        '--private', '-p',
        action='store_true',
        help="创建私有仓库"
    )
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help="自动确认所有提示"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="执行 dry run，不实际创建仓库"
    )

    args = parser.parse_args()

    print("🤖 GitHub API 自动化工具")
    print("=" * 60)

    # 检查是否提供了 GitHub 令牌
    github_token = args.token or os.environ.get('GITHUB_TOKEN')
    if not github_token:
        # 检查是否是帮助请求
        if any(arg in ['--help', '-h'] for arg in sys.argv):
            return 0

        github_token = input("🔑 请输入 GitHub 个人访问令牌 (PAT): ").strip()

        if not github_token:
            print("❌ 没有提供 GitHub 令牌，程序退出")
            return 1

    try:
        # 初始化自动化对象
        automation = GitHubAPIAutomation(github_token)

        # 设置 Git 凭证助手
        setup_git_credentials()

        # 项目配置
        repo_name = "github-learning-ai"
        repo_desc = "贾维斯式主动沟通AI学习系统"
        project_dir = os.path.dirname(os.path.abspath(__file__))

        print(f"\n📋 项目信息:")
        print(f"   仓库名称: {repo_name}")
        print(f"   描述: {repo_desc}")
        print(f"   项目目录: {project_dir}")

        # 检查仓库是否已存在
        if automation.check_repository_exists(repo_name):
            print(f"⚠️  仓库 '{repo_name}' 已存在")
            choice = input("是否要重新初始化并推送项目? (y/N): ").strip().lower()
            if choice != 'y':
                print("📋 程序终止")
                return 0

        # 安装项目依赖
        install_requirements()

        # 创建仓库
        repo_info = automation.create_repository(repo_name, repo_desc, private=False)
        if not repo_info:
            return 1

        repo_html_url, repo_ssh_url, repo_https_url = repo_info

        print(f"\n📦 仓库信息:")
        print(f"   URL: {repo_html_url}")
        print(f"   SSH: {repo_ssh_url}")
        print(f"   HTTPS: {repo_https_url}")

        # 初始化本地仓库并推送到远程
        if automation.initialize_and_push_repo(project_dir, repo_name, repo_https_url):
            print("\n🎉 项目发布成功!")
            print(f"✅ GitHub 仓库: {repo_html_url}")
            return 0
        else:
            print("\n❌ 项目发布失败")
            return 1

    except Exception as e:
        print(f"\n🚨 程序执行出错: {e}")
        import traceback
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
