@echo off
chcp 65001 >/dev/null
echo [92m🚀 开始发布项目到GitHub[0m
echo ==========================================

:: 检查Git状态
echo [94m📊 检查Git状态...[0m
git status --porcelain > temp.txt
if %ERRORLEVEL% neq 0 (
    echo [91m❌ Git命令执行失败[0m
    pause
    exit /b 1
)

for /f %%i in (temp.txt) do (
    if not "%%i"=="" (
        echo [91m❌ 发现未提交的更改，请先提交[0m
        git status
        del temp.txt
        pause
        exit /b 1
    )
)

del temp.txt
echo [92m✅ Git工作树干净[0m

:: 检查是否有远程仓库
echo.
echo [94m🔍 检查远程仓库...[0m
git remote -v | findstr "origin" > temp.txt
if %ERRORLEVEL% neq 0 (
    echo [93m⚠️  未配置远程仓库[0m
    echo 请按照以下步骤配置：
    echo 1. 访问 https://github.com/new 创建仓库
    echo 2. 命名为: github-learning-ai
    echo 3. 复制以下命令执行：
    echo    git remote add origin git@github.com:your-username/github-learning-ai.git
    del temp.txt
    pause
    exit /b 1
)

:: 推送代码
echo.
echo [94m📤 推送到GitHub...[0m
echo 正在推送到 main 分支...
git push origin main
if %ERRORLEVEL% neq 0 (
    echo [91m❌ 推送失败，请检查网络连接和GitHub配置[0m
    pause
    exit /b 1
)

:: 检查标签
echo.
echo [94m🏷️  检查发布标签...[0m
git tag -l "v1.0.0" > temp.txt
if %ERRORLEVEL% neq 0 (
    git tag v1.0.0
    git push --tags
    echo [92m✅ 标签 v1.0.0 创建并推送成功[0m
) else (
    echo [92m✅ 标签 v1.0.0 已存在[0m
)

del temp.txt

:: 完成
echo.
echo [92m🎉 项目发布成功！[0m
echo ==========================================
echo [96m📦 项目已成功发布到 GitHub:[0m
echo [96m🌐 https://github.com/your-username/github-learning-ai[0m
echo.
echo [93m📖 下一步：[0m
echo 1. 访问仓库页面
echo 2. 点击 Releases → Draft a new release
echo 3. 输入版本号 v1.0.0
echo 4. 添加发布说明
echo 5. 点击 Publish release

pause
