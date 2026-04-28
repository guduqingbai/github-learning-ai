@echo off
chcp 65001 >nul
title 系统测试脚本

echo 🎯 系统测试脚本
echo ====================================================

echo.
echo 1. 测试主动沟通功能
python jarvis_active.py --test

if %errorlevel% neq 0 (
    echo ❌ 测试失败
    pause
    exit /b 1
)

echo.
echo 2. 检查数据文件
if exist "data\experts.json" (
    if exist "data\knowledge_base.json" (
        echo ✅ 专家和知识数据文件存在
    ) else (
        echo ❌ 知识数据文件缺失
        pause
        exit /b 1
    )
) else (
    echo ❌ 专家数据文件缺失
    pause
    exit /b 1
)

echo.
echo 3. 检查监控系统进程
tasklist | findstr python >nul
if %errorlevel% equ 0 (
    echo ✅ Python进程正在运行
) else (
    echo ⚠️  Python进程未运行
)

echo.
echo 🎉 系统测试完成！

pause
