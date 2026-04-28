#!/bin/bash

echo "🎯 系统测试脚本"
echo "===================================================="

# 测试主动沟通功能
echo -e "\n1. 测试主动沟通功能"
python jarvis_active.py --test

# 检查是否需要调整超时
if [ $? -ne 0 ]; then
    echo "❌ 测试失败"
    exit 1
fi

# 检查数据文件
echo -e "\n2. 检查数据文件"
if [ -f "data/experts.json" ] && [ -f "data/knowledge_base.json" ]; then
    echo "✅ 专家和知识数据文件存在"
else
    echo "❌ 数据文件缺失"
    exit 1
fi

# 检查进程
echo -e "\n3. 检查监控系统进程"
python_count=$(ps aux | grep python | grep -v grep | wc -l)

if [ $python_count -ge 1 ]; then
    echo "✅ Python进程正在运行"
else
    echo "⚠️  Python进程未运行"
fi

echo -e "\n🎉 系统测试完成！"
