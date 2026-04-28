#!/bin/bash
# 项目发布脚本

echo "🚀 开始发布项目到GitHub"
echo "=========================================="

# 检查Git状态
echo "📊 检查Git状态..."
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ 发现未提交的更改，请先提交"
    git status
    exit 1
fi

echo "✅ Git工作树干净"

# 检查是否有远程仓库
echo -e "\n🔍 检查远程仓库..."
if ! git remote -v | grep -q "origin"; then
    echo "⚠️  未配置远程仓库"
    echo "请按照以下步骤配置："
    echo "1. 访问 https://github.com/new 创建仓库"
    echo "2. 命名为: github-learning-ai"
    echo "3. 复制以下命令执行："
    echo "   git remote add origin git@github.com:your-username/github-learning-ai.git"
    exit 1
fi

# 推送代码
echo -e "\n📤 推送到GitHub..."
echo "正在推送到 master 分支..."
git push origin master

# 检查标签
echo -e "\n🏷️  检查发布标签..."
if ! git tag -l "v1.0.0"; then
    git tag v1.0.0
    git push --tags
    echo "✅ 标签 v1.0.0 创建并推送成功"
else
    echo "✅ 标签 v1.0.0 已存在"
fi

# 完成
echo -e "\n🎉 项目发布成功！"
echo "=========================================="
echo "📦 项目已成功发布到 GitHub:"
echo "🌐 https://github.com/your-username/github-learning-ai"
echo -e "\n📖 下一步："
echo "1. 访问仓库页面"
echo "2. 点击 Releases → Draft a new release"
echo "3. 输入版本号 v1.0.0"
echo "4. 添加发布说明"
echo "5. 点击 Publish release"

