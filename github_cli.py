#!/usr/bin/env python3
"""使用 GitHub CLI 的自动化工具"""

import subprocess
import os
import sys
import json
import argparse


def run_command(cmd, check=True, capture_output=True):
    """运行命令"""
    try:
        result = subprocess.run(cmd, shell=True, check=check,
                             capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令失败: {e.cmd}")
        print(f"错误: {e.stderr}")
        return None


def check_gh_cli():
    """检查 GitHub CLI 是否安装"""
    result = run_command('gh --version', check=False)

    if result and result.returncode == 0:
        print(f"✅ GitHub CLI 已安装: {result.stdout.strip()}")
        return True

    print("❌ GitHub CLI 未安装")
    print("请从 https://cli.github.com/ 下载并安装 GitHub CLI")
    return False


def check_gh_auth():
    """检查是否已认证"""
    result = run_command('gh auth status', check=False)

    if result and result.returncode == 0:
        print("✅ GitHub CLI 认证成功")
        print(result.stdout)
        return True

    print("⚠️  GitHub CLI 未认证")
    return False


def authenticate_gh_cli(token=None):
    """认证 GitHub CLI"""
    if token:
        result = run_command(f'gh auth login --with-token <<< "{token}"', check=True)
    else:
        result = run_command('gh auth login', check=True)

    return result is not None and result.returncode == 0


def create_github_repo(repo_name, repo_desc="", private=False, org=None):
    """使用 GitHub CLI 创建仓库"""
    cmd = f'gh repo create {repo_name} --description "{repo_desc}"'

    if private:
        cmd += ' --private'
    else:
        cmd += ' --public'

    if org:
        cmd += f' --org {org}'

    cmd += ' --gitignore Python --license MIT --confirm'

    print(f"🚀 创建仓库命令: {cmd}")

    result = run_command(cmd, check=True)

    if result and result.returncode == 0:
        print("✅ 仓库创建成功")
        return True

    return False


def push_to_repo(repo_name, branch="main"):
    """推送到远程仓库"""
    print("📤 推送到远程仓库")

    result = run_command(f'git remote add origin https://github.com/{get_gh_user()}/{repo_name}.git', check=False)

    result = run_command('git branch -M main', check=False)

    result = run_command(f'git push -u origin {branch}', check=True)

    if result and result.returncode == 0:
        print("✅ 推送成功")
        return True

    return False


def get_gh_user():
    """获取当前 GitHub 用户"""
    result = run_command('gh api user | jq -r .login', check=False)

    if result and result.returncode == 0:
        return result.stdout.strip()

    return None


def list_repos():
    """列出仓库"""
    result = run_command('gh repo list', check=False)

    if result and result.returncode == 0:
        print(result.stdout)
        return True

    return False


def check_repo_exists(repo_name):
    """检查仓库是否存在"""
    user = get_gh_user()
    cmd = f'gh api repos/{user}/{repo_name}'

    result = run_command(cmd, check=False)

    if result and result.returncode == 200:
        print(f"✅ 仓库 {repo_name} 已存在")
        return True

    print(f"❌ 仓库 {repo_name} 不存在")
    return False


def create_branch(branch_name):
    """创建新分支"""
    print(f"🌿 创建分支: {branch_name}")
    result = run_command(f'git checkout -b {branch_name}', check=True)
    return result and result.returncode == 0


def merge_branch(source_branch, target_branch="main"):
    """合并分支"""
    print(f"🔄 合并分支 {source_branch} 到 {target_branch}")
    result = run_command(f'git checkout {target_branch} && git merge {source_branch}', check=True)
    return result and result.returncode == 0


def create_pull_request(title, body, head_branch, base_branch="main"):
    """创建拉取请求"""
    cmd = f'gh pr create --title "{title}" --body "{body}" --head {head_branch} --base {base_branch}'
    print(f"🔗 创建 PR: {cmd}")

    result = run_command(cmd, check=True)
    return result and result.returncode == 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="GitHub CLI 自动化工具"
    )

    parser.add_argument(
        'command',
        choices=['create', 'push', 'list', 'check', 'branch', 'merge', 'pr'],
        help="执行的命令"
    )

    parser.add_argument(
        '--repo', '-r',
        default="github-learning-ai",
        help="仓库名称"
    )

    parser.add_argument(
        '--desc', '-d',
        default="贾维斯式主动沟通AI学习系统",
        help="仓库描述"
    )

    parser.add_argument(
        '--branch', '-b',
        default="main",
        help="分支名称"
    )

    parser.add_argument(
        '--private', '-p',
        action='store_true',
        help="创建私有仓库"
    )

    parser.add_argument(
        '--org',
        help="组织名称"
    )

    parser.add_argument(
        '--token', '-t',
        help="GitHub 个人访问令牌"
    )

    parser.add_argument(
        '--title',
        help="拉取请求标题"
    )

    parser.add_argument(
        '--body',
        help="拉取请求正文"
    )

    parser.add_argument(
        '--head',
        help="源分支"
    )

    parser.add_argument(
        '--base',
        default="main",
        help="目标分支"
    )

    args = parser.parse_args()

    print("🤖 GitHub CLI 自动化工具")
    print("=" * 60)

    if not check_gh_cli():
        return 1

    if not check_gh_auth():
        if args.token:
            authenticate_gh_cli(args.token)
        else:
            print("❌ 需要 GitHub 认证")
            return 1

    if args.command == 'create':
        if create_github_repo(args.repo, args.desc, args.private, args.org):
            print("✅ 仓库创建成功")

    elif args.command == 'push':
        if push_to_repo(args.repo, args.branch):
            print("✅ 推送成功")

    elif args.command == 'list':
        list_repos()

    elif args.command == 'check':
        check_repo_exists(args.repo)

    elif args.command == 'branch':
        if create_branch(args.branch):
            print(f"✅ 分支 '{args.branch}' 创建成功")

    elif args.command == 'merge':
        if merge_branch(args.branch, args.base):
            print(f"✅ 分支 '{args.branch}' 合并到 '{args.base}' 成功")

    elif args.command == 'pr':
        if args.title and args.body and args.head:
            if create_pull_request(args.title, args.body, args.head, args.base):
                print("✅ 拉取请求创建成功")
        else:
            print("❌ 缺少拉取请求的标题、正文或源分支")
            return 1

    else:
        print(f"❌ 未知命令: {args.command}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
