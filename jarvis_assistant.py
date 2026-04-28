#!/usr/bin/env python3
"""
🤖 Jarvis AI 助手 - 智能项目学习管家
具备主动性和自然语言交互能力，类似钢铁侠中的贾维斯
"""

import click
import json
import os
from pathlib import Path
import random
import time

# 数据目录
DATA_DIR = Path("data")

class JarvisAssistant:
    """智能项目学习管家"""

    def __init__(self):
        self.learning_plan = []
        self.project_tracking = {}
        self.user_preferences = {}
        self.conversation_history = []
        self.load_data()

    def load_data(self):
        """加载学习数据"""
        # 加载项目跟踪数据
        tracking_file = DATA_DIR / "jarvis_tracking.json"
        if tracking_file.exists():
            with open(tracking_file, 'r', encoding='utf-8') as f:
                self.project_tracking = json.load(f)

        # 加载用户偏好
        preferences_file = DATA_DIR / "jarvis_preferences.json"
        if preferences_file.exists():
            with open(preferences_file, 'r', encoding='utf-8') as f:
                self.user_preferences = json.load(f)

    def save_data(self):
        """保存数据"""
        tracking_file = DATA_DIR / "jarvis_tracking.json"
        with open(tracking_file, 'w', encoding='utf-8') as f:
            json.dump(self.project_tracking, f, ensure_ascii=False, indent=2)

        preferences_file = DATA_DIR / "jarvis_preferences.json"
        with open(preferences_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_preferences, f, ensure_ascii=False, indent=2)

    def analyze_user_learning_style(self):
        """分析用户学习风格"""
        if not self.project_tracking:
            return "探索型学习"

        # 基于学习历史分析学习风格
        completed_projects = [p for p in self.project_tracking.values() if p.get('completed')]
        if len(completed_projects) > 10:
            return "系统型学习"
        return "深度型学习"

    def suggest_learning_path(self):
        """建议学习路径"""
        learning_style = self.analyze_user_learning_style()

        if learning_style == "探索型学习":
            return """
🚀 探索型学习路径：
1. 每天学习2-3个不同领域的项目
2. 重点关注项目创新点和技术栈
3. 记录项目特点和应用场景
4. 定期回顾总结，找到兴趣方向
            """.strip()

        elif learning_style == "系统型学习":
            return """
📚 系统型学习路径：
1. 选择一个核心领域深入学习
2. 系统地学习相关项目和技术
3. 构建项目作品集
4. 参与社区贡献和开源项目
            """.strip()

        else:
            return """
💎 深度型学习路径：
1. 选择2-3个高质量项目深入研究
2. 阅读源码和文档
3. 复现项目功能
4. 添加创新功能或优化现有功能
            """.strip()

    def suggest_next_project(self):
        """建议下一个学习项目"""
        # 加载探索结果
        exploration_file = DATA_DIR / "github_exploration.json"
        if not exploration_file.exists():
            return "❌ 未找到项目数据，请先运行探索功能"

        with open(exploration_file, 'r', encoding='utf-8') as f:
            exploration_data = json.load(f)

        # 获取所有项目
        all_projects = []
        for category in exploration_data:
            all_projects.extend(category['items'])

        # 过滤已学习项目
        completed_projects = [p['name'] for p in self.project_tracking.values() if p.get('completed')]
        available_projects = [p for p in all_projects if p['name'] not in completed_projects]

        if available_projects:
            # 按重要性排序（Stars * 0.7 + Forks * 0.3）
            available_projects.sort(key=lambda x: x['stargazers_count'] * 0.7 + x['forks_count'] * 0.3, reverse=True)

            project = available_projects[0]
            return f"""
🎯 推荐学习项目：{project['name']}
   🌟 Stars: {project['stargazers_count']}
   📊 Forks: {project['forks_count']}
   🔗 {project['html_url']}
   📝 {project['description'][:100]}...
            """.strip()

        return "✅ 您已经学完了所有推荐项目！建议探索新的技术领域"

    def track_learning_progress(self, project_name):
        """跟踪学习进度"""
        if project_name not in self.project_tracking:
            self.project_tracking[project_name] = {
                'name': project_name,
                'start_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'completed': False,
                'notes': []
            }
        return self.project_tracking[project_name]

    def add_project_note(self, project_name, note):
        """添加项目笔记"""
        if project_name not in self.project_tracking:
            self.track_learning_progress(project_name)

        self.project_tracking[project_name]['notes'].append({
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'content': note
        })
        self.save_data()

    def mark_project_completed(self, project_name):
        """标记项目完成"""
        if project_name in self.project_tracking:
            self.project_tracking[project_name]['completed'] = True
            self.project_tracking[project_name]['completed_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
            self.save_data()

    def get_learning_summary(self):
        """获取学习总结"""
        completed = [p for p in self.project_tracking.values() if p.get('completed')]
        in_progress = [p for p in self.project_tracking.values() if not p.get('completed')]

        if self.project_tracking:
            progress = (len(completed)/len(self.project_tracking))*100
        else:
            progress = 0.0

        return f"""
📊 学习进度总结：
   • 已完成项目: {len(completed)}
   • 学习中项目: {len(in_progress)}
   • 总学习时间: {self.calculate_total_learning_time()}小时
   • 学习进度: {progress:.1f}%
            """.strip()

    def calculate_total_learning_time(self):
        """计算总学习时间（估算）"""
        # 简单估算：每个项目学习时间为2小时
        return len(self.project_tracking) * 2

    def respond_to_natural_language(self, query):
        """自然语言响应"""
        query = query.lower()

        # 学习相关问题
        if '学习' in query or '项目' in query or '推荐' in query:
            return self.suggest_next_project()

        elif '进度' in query or '总结' in query or '学习时间' in query:
            return self.get_learning_summary()

        elif '路径' in query or '计划' in query or '方法' in query:
            return self.suggest_learning_path()

        elif '笔记' in query or '记录' in query:
            return "📝 我可以帮助您记录学习笔记。请使用 `add_note` 命令。"

        elif '完成' in query or '结束' in query:
            return "✅ 请使用 `complete` 命令来标记项目完成。"

        elif '帮助' in query or '功能' in query:
            return self.get_help()

        else:
            responses = [
                "🤔 我不太明白您的意思。请使用 `help` 命令查看可用功能。",
                "💡 我可以帮助您学习项目、管理进度、获取学习建议。",
                "🚀 告诉我您想学习什么，我会为您提供个性化建议！"
            ]
            return random.choice(responses)

    def get_help(self):
        """获取帮助信息"""
        return """
🤖 Jarvis AI 助手功能：
   • `suggest` - 建议下一个学习项目
   • `path` - 建议学习路径
   • `summary` - 查看学习进度
   • `add_note <项目名> <笔记>` - 添加学习笔记
   • `complete <项目名>` - 标记项目完成
   • `help` - 查看帮助信息
            """.strip()

@click.group()
def cli():
    """🤖 Jarvis AI 助手 - 智能项目学习管家"""
    pass

@cli.command()
def suggest():
    """🎯 建议下一个学习项目"""
    jarvis = JarvisAssistant()
    click.echo(jarvis.suggest_next_project())

@cli.command()
def path():
    """📚 建议学习路径"""
    jarvis = JarvisAssistant()
    click.echo(jarvis.suggest_learning_path())

@cli.command()
def summary():
    """📊 查看学习进度总结"""
    jarvis = JarvisAssistant()
    click.echo(jarvis.get_learning_summary())

@cli.command()
@click.argument('project_name')
@click.argument('note')
def add_note(project_name, note):
    """📝 添加学习笔记"""
    jarvis = JarvisAssistant()
    jarvis.add_project_note(project_name, note)
    click.echo("✅ 笔记已保存")

@cli.command()
@click.argument('project_name')
def complete(project_name):
    """✅ 标记项目完成"""
    jarvis = JarvisAssistant()
    jarvis.mark_project_completed(project_name)
    click.echo(f"✅ 项目 '{project_name}' 已标记为完成")

@cli.command()
@click.argument('query')
def chat(query):
    """💬 自然语言聊天"""
    jarvis = JarvisAssistant()
    click.echo(jarvis.respond_to_natural_language(query))

@cli.command()
def start():
    """🚀 启动智能助手"""
    jarvis = JarvisAssistant()
    click.echo("🤖 您好！我是Jarvis AI助手，您的智能项目学习管家")
    click.echo("=" * 60)

    # 检查学习进度
    if not jarvis.project_tracking:
        click.echo("\n👋 我注意到您还没有开始学习项目")
        click.echo("🎯 让我为您推荐第一个学习项目")
        click.echo(jarvis.suggest_next_project())

        click.echo("\n📚 您可以按照这个路径学习：")
        click.echo(jarvis.suggest_learning_path())

        click.echo("\n💡 建议每天学习2-3个项目，保持学习节奏")
    else:
        click.echo(f"\n📊 您已经学习了 {len(jarvis.project_tracking)} 个项目")
        click.echo("🚀 让我们继续学习之旅")
        click.echo(jarvis.suggest_next_project())

    click.echo("\n💬 您可以使用 `chat` 命令与我自然语言交流")

if __name__ == '__main__':
    # 确保数据目录存在
    if not DATA_DIR.exists():
        DATA_DIR.mkdir()

    cli()
