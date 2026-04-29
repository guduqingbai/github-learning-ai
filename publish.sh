#!/bin/bash
# GitHub项目发布自动化脚本

set -e

# 项目配置
PROJECT_NAME="github-learning"
REPO_NAME="github-learning-ai"
REPO_DESC="贾维斯式主动沟通AI学习系统"
BRANCH="main"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 打印信息
echo -e "${GREEN}🚀 GitHub项目发布自动化工具${NC}"
echo "===================================="

# 检查项目根目录
if [ ! -f "README.md" ] || [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 检查依赖是否已安装
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ git 未安装${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ Python 未安装${NC}"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建${NC}"
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✅ 虚拟环境创建成功${NC}"
fi

# 激活虚拟环境
echo -e "${YELLOW}🔧 激活虚拟环境${NC}"
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    source venv/Scripts/activate
fi

# 安装依赖
echo -e "${YELLOW}📦 安装项目依赖${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✅ 依赖安装完成${NC}"

# 检查 Git 状态
echo -e "${YELLOW}📋 检查 Git 状态${NC}"
if ! git status &> /dev/null; then
    echo -e "${RED}❌ 项目未初始化 Git${NC}"
    echo "是否初始化 Git? (y/N):"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        git init
        git config user.name "GitHub Automation"
        git config user.email "automation@example.com"
        git add .
        git commit -m "Initial commit"
    else
        exit 1
    fi
fi

# 检查远程仓库
echo -e "${YELLOW}📡 检查远程仓库配置${NC}"
if ! git remote -v | grep -q "origin"; then
    echo -e "${RED}❌ 未配置远程仓库${NC}"
    echo "是否要创建 GitHub 仓库? (y/N):"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        $PYTHON_CMD github_api_automation.py --token "$GITHUB_TOKEN" --repo "$REPO_NAME" --desc "$REPO_DESC"
    else
        exit 1
    fi
fi

# 检查分支
echo -e "${YELLOW}🌿 检查分支${NC}"
if [ "$(git rev-parse --abbrev-ref HEAD)" != "$BRANCH" ]; then
    echo -e "${YELLOW}⚠️  当前不在 ${BRANCH} 分支${NC}"
    echo "是否切换到 ${BRANCH} 分支? (y/N):"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        git checkout "$BRANCH" || git checkout -b "$BRANCH"
    else
        exit 1
    fi
fi

# 拉取最新代码
echo -e "${YELLOW}🔄 拉取最新代码${NC}"
git pull origin "$BRANCH"

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  发现未提交的更改${NC}"
    echo "是否提交这些更改? (y/N):"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        git add .
        git commit -m "更新项目 - $(date +"%Y-%m-%d %H:%M:%S")"
    fi
fi

# 推送到远程仓库
echo -e "${YELLOW}📤 推送到远程仓库${NC}"
git push origin "$BRANCH"

echo -e "${GREEN}🎉 项目发布成功!${NC}"
echo "===================================="

# 显示项目信息
echo -e "${YELLOW}📋 项目信息:${NC}"
echo "项目名称: $PROJECT_NAME"
echo "仓库名称: $REPO_NAME"
echo "描述: $REPO_DESC"
echo "分支: $BRANCH"
echo -e "${GREEN}✅ 发布完成${NC}"
