#!/usr/bin/env python3
"""
🎯 GitHub 项目分析系统
帮助我们分析哪些项目能提升能力、哪些能二次开发、哪些是市场空白
"""

import click
import requests
import json
import os
from pathlib import Path
import time

# GitHub API 配置
GITHUB_API = "https://api.github.com"
# 添加API密钥支持，可在环境变量中设置
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

# 创建数据目录
DATA_DIR = Path("data")
if not DATA_DIR.exists():
    DATA_DIR.mkdir()

# 避免API限流的延迟时间
REQUEST_DELAY = 2.0

@click.group()
def cli():
    """
    🎯 GitHub 项目分析系统
    分析哪些项目能提升能力、哪些能二次开发、哪些是市场空白
    """
    pass

@cli.command()
@click.argument('keywords')
@click.option('--language', '-l', help='项目语言')
@click.option('--limit', '-L', default=20, help='搜索结果数量')
def search(keywords, language, limit):
    """
    🔍 搜索 GitHub 项目
    """
    click.echo(f"🎯 搜索 GitHub 项目: {keywords}")

    # 构建搜索查询
    if language:
        query = f"{keywords} language:{language} stars:>1000"
    else:
        query = f"{keywords} stars:>1000"

    try:
        url = f"{GITHUB_API}/search/repositories?q={query}&sort=stars&order=desc&per_page={limit}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)

        data = response.json()

        click.echo(f"✅ 找到 {data['total_count']} 个项目")
        click.echo("=" * 60)

        # 保存到文件
        filename = DATA_DIR / f"github_search_{keywords.replace(' ', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        click.echo(f"📊 结果已保存到: {filename}")

        # 显示前5个项目
        click.echo("\n🏆 最受欢迎的项目:")
        for i, item in enumerate(data['items'][:5], 1):
            click.echo(f"{i}. {item['name']}")
            click.echo(f"   🌟 Stars: {item['stargazers_count']}")
            click.echo(f"   📊 Forks: {item['forks_count']}")
            click.echo(f"   🔗 {item['html_url']}")

            description = item['description']
            if len(description) > 100:
                description = description[:100] + "..."
            click.echo(f"   📝 {description}")

        return data

    except Exception as e:
        click.echo(f"❌ 搜索失败: {e}")
        return None

@cli.command()
@click.argument('username')
@click.option('--limit', '-l', default=5, help='项目数量')
def user(username, limit):
    """
    👤 查看用户项目
    """
    click.echo(f"🎯 查看用户 {username} 的项目")

    try:
        url = f"{GITHUB_API}/users/{username}/repos?per_page={limit}&sort=updated"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)

        repos = response.json()

        click.echo(f"✅ 找到 {len(repos)} 个项目")
        click.echo("=" * 60)

        filename = DATA_DIR / f"github_user_{username}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(repos, f, ensure_ascii=False, indent=2)
        click.echo(f"📊 结果已保存到: {filename}")

        click.echo("\n🏆 项目列表:")
        for i, repo in enumerate(repos[:min(limit, len(repos))], 1):
            click.echo(f"{i}. {repo['name']}")
            click.echo(f"   🌟 Stars: {repo['stargazers_count']}")
            click.echo(f"   📊 Forks: {repo['forks_count']}")
            click.echo(f"   🔗 {repo['html_url']}")

            description = repo['description']
            if description and len(description) > 100:
                description = description[:100] + "..."
            click.echo(f"   📝 {description}")

    except Exception as e:
        click.echo(f"❌ 获取用户项目失败: {e}")

@cli.command()
@click.argument('repos')
def analyze(repos):
    """
    📊 分析项目的商业价值
    """
    click.echo(f"🎯 分析项目: {repos}")

    try:
        repo_owner, repo_name = repos.split("/")
        url = f"{GITHUB_API}/repos/{repo_owner}/{repo_name}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)

        repo = response.json()

        click.echo(f"✅ 项目分析完成")
        click.echo("=" * 60)

        click.echo(f"🏆 项目: {repo['name']}")
        click.echo(f"   🌟 Stars: {repo['stargazers_count']}")
        click.echo(f"   📊 Forks: {repo['forks_count']}")
        click.echo(f"   👥 Watchers: {repo['watchers']}")
        click.echo(f"   🔗 {repo['html_url']}")

        description = repo['description']
        if len(description) > 150:
            description = description[:150] + "..."
        click.echo(f"   📝 {description}")

        # 分析商业价值
        analysis = analyze_business_value(repo)

        click.echo(f"\n💰 商业价值分析:")
        for key, value in analysis.items():
            click.echo(f"   • {key}: {value}")

        filename = DATA_DIR / f"github_analysis_{repo['name']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "repo": repo,
                "analysis": analysis
            }, f, ensure_ascii=False, indent=2)
        click.echo(f"\n📊 分析结果已保存到: {filename}")

    except Exception as e:
        click.echo(f"❌ 项目分析失败: {e}")

def analyze_business_value(repo):
    """
    💰 分析项目商业价值
    """
    analysis = {
        "市场需求": "低",
        "技术复杂度": "低",
        "可维护性": "中",
        "二次开发潜力": "中",
        "商业价值": "低"
    }

    # 根据项目特点评估
    if repo.get('description'):
        description = repo['description'].lower()
        if 'learn' in description or 'education' in description or 'teach' in description:
            analysis['市场需求'] = "高"
            analysis['商业价值'] = "高"

        if 'ai' in description or 'machine learning' in description or 'deep learning' in description:
            analysis['技术复杂度'] = "高"
            analysis['二次开发潜力'] = "高"
            analysis['商业价值'] = "高"

        if 'finance' in description or 'investment' in description or 'money' in description:
            analysis['市场需求'] = "高"
            analysis['商业价值'] = "高"

    # 根据项目受欢迎程度评估
    stars = repo['stargazers_count']
    forks = repo['forks_count']

    if stars > 10000:
        analysis['市场需求'] = "高"
        analysis['商业价值'] = "高"
    elif stars > 5000:
        analysis['市场需求'] = "中"
        analysis['商业价值'] = "中"

    if forks > 1000:
        analysis['可维护性'] = "高"
        analysis['二次开发潜力'] = "高"

    return analysis

@cli.command()
def explore():
    """
    🚀 探索市场空白项目
    """
    click.echo("🎯 探索市场空白项目")
    click.echo("=" * 60)

    categories = [
        {"name": "智能学习系统", "keywords": "learning"},
        {"name": "自动化工作流", "keywords": "workflow"},
        {"name": "智能投资助手", "keywords": "investment"},
        {"name": "内容生成", "keywords": "content"},
        {"name": "数据分析", "keywords": "data"}
    ]

    results = []
    for category in categories:
        click.echo(f"🔍 搜索 {category['name']}")

        try:
            query = f"{category['keywords']} language:Python stars:>1000"
            url = f"{GITHUB_API}/search/repositories?q={query}&sort=stars&order=desc&per_page=10"
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            time.sleep(REQUEST_DELAY)

            data = response.json()
            results.append({
                "category": category['name'],
                "count": data['total_count'],
                "items": data['items'][:5]
            })

            click.echo(f"✅ 找到 {data['total_count']} 个项目")
            click.echo("-" * 40)

        except Exception as e:
            click.echo(f"❌ 搜索失败: {e}")

    # 保存结果
    filename = DATA_DIR / "github_exploration.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    click.echo(f"\n📊 探索结果已保存到: {filename}")

    # 显示分析
    click.echo("\n📊 市场分析:")
    for result in results:
        click.echo(f"\n🏆 {result['category']}:")
        click.echo(f"   📊 项目数量: {result['count']}")
        if result['items']:
            click.echo(f"   🏆 最受欢迎项目: {result['items'][0]['name']}")
            click.echo(f"      🌟 Stars: {result['items'][0]['stargazers_count']}")
            click.echo(f"      🔗 {result['items'][0]['html_url']}")

@cli.command()
def analyze_local():
    """
    📊 分析本地存储的项目数据
    """
    click.echo("🎯 分析本地项目数据")
    click.echo("=" * 60)

    # 读取探索结果
    exploration_file = DATA_DIR / "github_exploration.json"
    if not exploration_file.exists():
        click.echo("❌ 未找到探索结果文件")
        return

    with open(exploration_file, 'r', encoding='utf-8') as f:
        exploration_data = json.load(f)

    click.echo(f"✅ 找到 {len(exploration_data)} 个类别")

    # 分析每个类别的项目
    for category in exploration_data:
        click.echo(f"\n🏆 {category['category']}:")
        click.echo(f"   📊 项目数量: {category['count']}")

        if category['items']:
            click.echo(f"   🏆 最受欢迎项目: {category['items'][0]['name']}")
            click.echo(f"      🌟 Stars: {category['items'][0]['stargazers_count']}")
            click.echo(f"      📊 Forks: {category['items'][0]['forks_count']}")
            click.echo(f"      🔗 {category['items'][0]['html_url']}")

            # 商业价值分析
            analysis = analyze_business_value(category['items'][0])
            click.echo(f"      💰 商业价值: {analysis['商业价值']}")
            click.echo(f"      🚀 二次开发潜力: {analysis['二次开发潜力']}")

    # 统计所有项目
    all_projects = []
    for category in exploration_data:
        all_projects.extend(category['items'])

    click.echo(f"\n📊 总项目统计:")
    click.echo(f"   • 总项目数: {len(all_projects)}")

    # 按stars排序
    sorted_projects = sorted(all_projects, key=lambda x: x['stargazers_count'], reverse=True)
    click.echo(f"\n🏆 前5个最受欢迎项目:")
    for i, project in enumerate(sorted_projects[:5], 1):
        click.echo(f"{i}. {project['name']} ({project['stargazers_count']} stars)")

@cli.command()
def info():
    """
    📊 系统信息
    """
    click.echo("🎯 GitHub 项目分析系统")
    click.echo("=" * 60)
    click.echo("🚀 功能特性:")
    click.echo("   • 🔍 GitHub 项目搜索")
    click.echo("   • 👤 用户项目分析")
    click.echo("   • 📊 项目商业价值分析")
    click.echo("   • 🚀 市场空白项目探索")
    click.echo("   • 💾 数据存储和管理")
    click.echo("   • 📊 本地项目数据分析")

    data_files = list(DATA_DIR.glob("*.json"))
    click.echo(f"\n📊 数据统计:")
    click.echo(f"   • 分析记录: {len(data_files)}")

    if len(data_files) > 0:
        click.echo("\n📝 数据文件:")
        for file in data_files:
            click.echo(f"   • {file.name}")

if __name__ == '__main__':
    cli()
