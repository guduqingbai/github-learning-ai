#!/usr/bin/env python3
"""
🎯 GitHub项目学习建议生成器
基于本地分析结果提供学习建议
"""

import json
import os
from pathlib import Path

# 数据目录
DATA_DIR = Path("data")

def load_exploration_data():
    """加载探索结果数据"""
    exploration_file = DATA_DIR / "github_exploration.json"
    if not exploration_file.exists():
        print("❌ 未找到探索结果文件")
        return None

    with open(exploration_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_projects(data):
    """分析项目并生成建议"""
    if not data:
        return

    all_projects = []
    for category in data:
        all_projects.extend(category['items'])

    # 按stars排序
    sorted_projects = sorted(all_projects, key=lambda x: x['stargazers_count'], reverse=True)

    print("🎯 GitHub项目学习建议")
    print("=" * 60)

    print("\n📊 总体分析:")
    print(f"   • 总项目数: {len(all_projects)}")
    print(f"   • 平均Stars: {sum(p['stargazers_count'] for p in all_projects) // len(all_projects)}")

    print("\n🏆 前10个最受欢迎项目:")
    for i, project in enumerate(sorted_projects[:10], 1):
        print(f"{i}. {project['name']}")
        print(f"   🌟 Stars: {project['stargazers_count']}")
        print(f"   📊 Forks: {project['forks_count']}")
        print(f"   🔗 {project['html_url']}")
        if project.get('description'):
            desc = project['description']
            if len(desc) > 100:
                desc = desc[:100] + "..."
            print(f"   📝 {desc}")
        print()

    print("🎓 学习建议:")
    print("=" * 60)

    print("\n🚀 优先学习项目:")
    print("   • transformers (NLP和AI领域的基础工具)")
    print("   • langflow (可视化工作流，适合快速开发原型)")
    print("   • funNLP (中文NLP工具包，适合中文应用开发)")
    print("   • qlib (量化投资工具，金融数据分析)")

    print("\n💡 创新项目机会:")
    print("   • 智能学习系统: 结合AI和教育的个性化学习平台")
    print("   • 自动化工作流: 无代码/低代码的流程自动化工具")
    print("   • 智能投资助手: 基于AI的投资决策支持系统")
    print("   • 内容生成: 自动化内容创作和优化工具")

    print("\n📚 学习资源建议:")
    print("   • GitHub README文件和文档")
    print("   • 项目示例代码和教程")
    print("   • 社区论坛和问题解答")

    print("\n🎯 每日学习计划:")
    print("   • 每天学习20个项目")
    print("   • 重点关注高Stars和高Forks的项目")
    print("   • 记录项目特点和学习笔记")
    print("   • 尝试使用项目代码进行实践")

if __name__ == "__main__":
    print("🎓 GitHub项目学习系统")
    print("正在加载项目数据...")

    data = load_exploration_data()
    if data:
        analyze_projects(data)
    else:
        print("❌ 无法加载项目数据")