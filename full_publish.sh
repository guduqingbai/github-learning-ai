#!/bin/bash
# 完整的项目发布脚本
# 处理仓库创建、代码推送和验证

set -e

# 项目配置
REPO_NAME="github-learning-ai"
REPO_DESC="贾维斯式主动沟通AI学习系统"
BRANCH="master"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 打印信息
echo -e "${GREEN}🚀 项目发布流程${NC}"
echo "===================================="

# 检查项目根目录
if [ ! -f "README.md" ] || [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 检查是否已安装 GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI 未安装${NC}"
    echo "请访问 https://cli.github.com/ 下载并安装 GitHub CLI"
    exit 1
fi

# 检查是否已登录 GitHub
echo -e "${YELLOW}🔐 检查 GitHub 认证状态${NC}"
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ 未登录 GitHub${NC}"
    echo -e "${YELLOW}是否需要登录? (y/N):${NC}"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        gh auth login
    else
        exit 1
    fi
fi
echo -e "${GREEN}✅ GitHub 认证成功${NC}"

# 检查仓库是否存在
echo -e "${YELLOW}📡 检查远程仓库是否存在${NC}"
CURRENT_USER=$(gh api user | jq -r .login)
if gh repo view "$CURRENT_USER/$REPO_NAME" &> /dev/null; then
    echo -e "${GREEN}✅ 仓库已存在${NC}"
else
    echo -e "${YELLOW}⚠️  仓库不存在，正在创建${NC}"
    gh repo create "$REPO_NAME" \
        --description "$REPO_DESC" \
        --public \
        --gitignore Python \
        --license MIT \
        --confirm
    echo -e "${GREEN}✅ 仓库创建成功${NC}"
fi

# 检查远程仓库配置
echo -e "${YELLOW}🔗 检查远程仓库配置${NC}"
if ! git remote -v | grep -q "origin"; then
    echo -e "${YELLOW}⚠️  未配置远程仓库，正在添加${NC}"
    git remote add origin "https://github.com/${CURRENT_USER}/${REPO_NAME}.git"
    echo -e "${GREEN}✅ 远程仓库配置成功${NC}"
fi

# 检查分支
echo -e "${YELLOW}🌿 检查当前分支${NC}"
if [ "$(git rev-parse --abbrev-ref HEAD)" != "$BRANCH" ]; then
    echo -e "${YELLOW}⚠️  不在主分支，正在创建/切换${NC}"
    git checkout -b "$BRANCH"
fi

# 推送到远程仓库
echo -e "${YELLOW}📤 推送到远程仓库${NC}"
if git push origin "$BRANCH"; then
    echo -e "${GREEN}✅ 推送成功${NC}"
else
    echo -e "${RED}❌ 推送失败${NC}"
    echo -e "${YELLOW}是否需要强制推送? (y/N):${NC}"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        git push -f origin "$BRANCH"
        echo -e "${GREEN}✅ 强制推送成功${NC}"
    else
        exit 1
    fi
fi

# 验证仓库内容
echo -e "${YELLOW}🔍 验证仓库内容${NC}"
if gh repo view "$CURRENT_USER/$REPO_NAME" --json description,stargazerCount,forkCount | jq .; then
    echo -e "${GREEN}✅ 仓库验证成功${NC}"
fi

# 显示成功信息
echo -e "${GREEN}🎉 项目发布成功!${NC}"
echo "===================================="
echo -e "${YELLOW}📋 项目信息:${NC}"
echo "仓库名称: $REPO_NAME"
echo "描述: $REPO_DESC"
echo "分支: $BRANCH"
echo "URL: https://github.com/${CURRENT_USER}/${REPO_NAME}"
echo -e "${GREEN}✅ 发布完成${NC}"
