#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目发布脚本 - 智能处理GitHub仓库发布过程
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path


class ProjectPublisher:
    """项目发布器"""

    def __init__(self, project_dir):
        """初始化发布器"""
        self.project_dir = Path(project_dir)
        self.repo_name = "github-learning-ai"
        self.gh_username = "吴文豪"
        self.remote_url = f"https://github.com/{self.gh_username}/{self.repo_name}.git"

    def run_command(self, cmd, cwd=None, shell=True, timeout=300):
        """运行命令并返回结果"""
        cwd = cwd or str(self.project_dir)
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return -1, "", "命令超时"
        except Exception as e:
            return -1, "", f"命令执行失败: {e}"

    def check_git_installed(self):
        """检查git是否安装"""
        print("🔍 检查git是否已安装...")
        return_code, stdout, stderr = self.run_command("git --version")
        if return_code == 0 and "git version" in stdout:
            print(f"✅ git已安装: {stdout.strip()}")
            return True
        else:
            print(f"❌ git未安装: {stderr}")
            return False

    def check_gh_cli_installed(self):
        """检查GitHub CLI是否安装"""
        print("🔍 检查GitHub CLI是否已安装...")
        return_code, stdout, stderr = self.run_command("gh --version")
        if return_code == 0 and "gh version" in stdout:
            print(f"✅ GitHub CLI已安装: {stdout.strip()}")
            return True
        else:
            print("⚠️  GitHub CLI未安装，将使用传统方式")
            return False

    def authenticate_with_gh_cli(self):
        """使用GitHub CLI认证"""
        print("🔐 使用GitHub CLI认证...")
        return_code, stdout, stderr = self.run_command("gh auth status")
        if return_code == 0 and "Logged in" in stdout:
            print("✅ 已认证")
            return True
        else:
            print("⚠️  未认证，尝试浏览器认证...")
            return_code, stdout, stderr = self.run_command("gh auth login")
            if return_code == 0:
                print("✅ 认证成功")
                return True
            else:
                print(f"❌ 认证失败: {stderr}")
                return False

    def check_repo_exists(self):
        """检查远程仓库是否存在"""
        print(f"🔍 检查远程仓库 {self.repo_name} 是否存在...")
        return_code, stdout, stderr = self.run_command(
            f"gh repo view {self.gh_username}/{self.repo_name}"
        )
        return return_code == 0

    def create_github_repo(self):
        """创建GitHub仓库"""
        print(f"🚀 创建GitHub仓库 {self.repo_name}...")
        cmd = (
            f"gh repo create {self.repo_name} "
            "--public "
            "--description \"AI学习助手项目 - 包含主动沟通、自我学习和专家系统功能\" "
            "--homepage \"https://github.com/吴文豪/github-learning-ai\" "
            "--source . "
            "--remote origin "
            "--push"
        )
        return_code, stdout, stderr = self.run_command(cmd)
        if return_code == 0:
            print("✅ 仓库创建成功")
            return True
        else:
            print(f"❌ 仓库创建失败: {stderr}")
            return False

    def configure_git_user(self):
        """配置git用户信息"""
        print("👤 配置git用户信息...")
        self.run_command("git config --global user.name \"吴文豪\"")
        self.run_command("git config --global user.email \"your.email@example.com\"")
        print("✅ 用户信息配置完成")

    def initialize_git_repo(self):
        """初始化git仓库"""
        print("🏗️  初始化git仓库...")
        if not (self.project_dir / ".git").exists():
            return_code, stdout, stderr = self.run_command("git init")
            if return_code == 0:
                print("✅ 仓库初始化成功")
            else:
                print(f"❌ 仓库初始化失败: {stderr}")
                return False
        else:
            print("✅ git仓库已存在")
        return True

    def check_remote_configured(self):
        """检查远程仓库是否已配置"""
        print("🔗 检查远程仓库配置...")
        return_code, stdout, stderr = self.run_command("git remote -v")
        if "origin" in stdout and self.repo_name in stdout:
            print("✅ 远程仓库已配置")
            return True
        else:
            print("⚠️  远程仓库未配置")
            return False

    def configure_remote_repo(self):
        """配置远程仓库"""
        print("🔗 配置远程仓库...")
        return_code, stdout, stderr = self.run_command(f"git remote add origin {self.remote_url}")
        if return_code == 0:
            print("✅ 远程仓库配置成功")
            return True
        else:
            print(f"⚠️  远程仓库已存在，尝试更新URL...")
            return_code, stdout, stderr = self.run_command(f"git remote set-url origin {self.remote_url}")
            if return_code == 0:
                print("✅ 远程仓库URL更新成功")
                return True
            else:
                print(f"❌ 远程仓库配置失败: {stderr}")
                return False

    def check_uncommitted_changes(self):
        """检查是否有未提交的更改"""
        print("📝 检查未提交的更改...")
        return_code, stdout, stderr = self.run_command("git status")
        if "nothing to commit, working tree clean" in stdout:
            print("✅ 工作区干净，没有未提交的更改")
            return True
        else:
            print("⚠️  有未提交的更改:")
            print(stdout)
            return False

    def commit_changes(self):
        """提交更改"""
        print("📦 提交所有更改...")
        return_code, stdout, stderr = self.run_command("git add .")
        if return_code != 0:
            print(f"❌ 添加文件失败: {stderr}")
            return False

        return_code, stdout, stderr = self.run_command("git commit -m \"项目完成 - 包含主动沟通、自我学习和专家系统功能\"")
        if return_code == 0:
            print("✅ 提交成功")
            return True
        elif "nothing to commit" in stderr:
            print("✅ 没有需要提交的更改")
            return True
        else:
            print(f"❌ 提交失败: {stderr}")
            return False

    def push_to_github(self):
        """推送到GitHub"""
        print("📤 推送到GitHub...")
        try:
            return_code, stdout, stderr = self.run_command("git push -u origin master", timeout=600)
            if return_code == 0:
                print("✅ 推送成功！")
                return True
            else:
                print(f"❌ 推送失败: {stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ 推送超时")
            return False

    def publish_project(self):
        """完整发布流程"""
        print("🚀 开始项目发布流程")
        print("=" * 60)

        # 检查git安装
        if not self.check_git_installed():
            return False

        # 检查并配置git用户信息
        self.configure_git_user()

        # 初始化git仓库
        if not self.initialize_git_repo():
            return False

        # 检查是否有未提交的更改
        if not self.check_uncommitted_changes():
            if not self.commit_changes():
                return False

        # 检查GitHub CLI
        if self.check_gh_cli_installed():
            # 使用GitHub CLI认证
            if self.authenticate_with_gh_cli():
                # 检查仓库是否存在
                if not self.check_repo_exists():
                    print("📦 远程仓库不存在，创建新仓库...")
                    if not self.create_github_repo():
                        return False
            else:
                print("⚠️  无法认证GitHub CLI")
        else:
            print("⚠️  GitHub CLI未安装，将尝试直接推送")

        # 检查远程仓库配置
        if not self.check_remote_configured():
            if not self.configure_remote_repo():
                return False

        # 尝试推送到GitHub
        print(f"📤 推送到远程仓库: {self.remote_url}")
        if self.push_to_github():
            print("\n🎉 项目发布成功！")
            print("=" * 60)
            print(f"📦 仓库地址: https://github.com/{self.gh_username}/{self.repo_name}")
            print("🌐 项目主页: https://github.com/吴文豪/github-learning-ai")
            print("🔗 克隆地址: git clone https://github.com/吴文豪/github-learning-ai.git")
            return True
        else:
            print("\n❌ 项目发布失败")
            print("=" * 60)
            print("🔍 可能的解决方法:")
            print("1. 检查网络连接")
            print("2. 确认您已在GitHub上创建了仓库")
            print("3. 检查是否有适当的权限")
            print("4. 尝试使用SSH方式推送")
            return False


def main():
    """主函数"""
    project_dir = Path(__file__).parent

    print("🤖 AI学习助手项目发布器")
    print("=" * 60)
    print(f"📂 项目目录: {project_dir}")

    publisher = ProjectPublisher(project_dir)

    # 执行发布流程
    success = publisher.publish_project()

    if success:
        print("\n✅ 项目发布任务完成！")
        return 0
    else:
        print("\n❌ 项目发布失败")
        print("🔗 请手动创建仓库:")
        print("1. 访问 https://github.com/new")
        print("2. 仓库名称: github-learning-ai")
        print("3. 描述: AI学习助手项目 - 包含主动沟通、自我学习和专家系统功能")
        print("4. 选择公开仓库")
        print("5. 创建仓库后，运行 git push -u origin master")
        return 1


if __name__ == "__main__":
    sys.exit(main())
