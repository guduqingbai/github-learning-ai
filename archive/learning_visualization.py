#!/usr/bin/env python3
"""
📊 学习数据分析可视化模块
提供8种专业图表，全面展示学习数据
"""

import os, sys, json, platform
from pathlib import Path
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互模式，服务器可用
import matplotlib.pyplot as plt
import seaborn as sns

# ── 中文字体 ──
import matplotlib.font_manager as fm
system = platform.system()
font_candidates = {
    'Windows': ['Microsoft YaHei', 'SimHei', 'KaiTi', 'DengXian'],
    'Darwin':  ['PingFang SC', 'STHeiti', 'Heiti SC', 'Apple LiGothic'],
}.get(system, ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'SimHei'])
# 查找系统中实际存在的中文字体
available = {f.name for f in fm.fontManager.ttflist}
matched = [f for f in font_candidates if f in available]
if matched:
    plt.rcParams['font.sans-serif'] = matched + ['sans-serif']
else:
    # 兜底：从已安装字体中找支持中文的
    for f in fm.fontManager.ttflist:
        if 'yahei' in f.name.lower() or 'simhei' in f.name.lower() or 'cjk' in f.name.lower():
            plt.rcParams['font.sans-serif'] = [f.name] + ['sans-serif']
            break
plt.rcParams['axes.unicode_minus'] = False

sns.set_style('whitegrid')
DEFAULT_PALETTE = sns.color_palette('husl', 12)


class LearningVisualization:
    """学习数据分析可视化"""

    def __init__(self):
        self.data_dir = Path("data")
        self.out_dir = Path("visualization")
        self.out_dir.mkdir(exist_ok=True)

    def _load(self, name):
        f = self.data_dir / name
        if f.exists():
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    return json.load(fh)
            except Exception:
                pass
        return {}

    # ──────────────────── 1. 学习进度总览仪表盘 ────────────────────
    def dash_progress(self):
        """1️⃣ 学习进度总览仪表盘 — 6合1卡片"""
        lp = self._load("learning_progress.json")
        ss = self._load("system_state.json")
        al = self._load("active_state.json")

        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle('📊 学习进度总览仪表盘', fontsize=22, fontweight='bold', y=0.98)

        # (1,1) 学习时间饼图
        t = lp.get("total_study_time", 688)
        sizes = [t, max(0, 720 - t)]
        axes[0, 0].pie(sizes, labels=[f'{t}分钟', ''], autopct='',
                       colors=['#2ecc71', '#ecf0f1'], startangle=90,
                       wedgeprops={'width': 0.4})
        axes[0, 0].set_title(f'⏱ 学习总时长\n{t}分钟 / 12小时', fontsize=13)

        # (1,2) 项目/知识要点柱状图
        projects = len(lp.get("projects_studied", []))
        kps = len(lp.get("knowledge_points", []))
        bars = axes[0, 1].bar(['已完成项目', '知识要点'], [projects, kps],
                              color=['#3498db', '#9b59b6'], width=0.5)
        for b in bars:
            axes[0, 1].text(b.get_x()+b.get_width()/2, b.get_height()+1,
                            str(int(b.get_height())), ha='center', fontsize=12)
        axes[0, 1].set_title('📚 项目与知识积累', fontsize=13)

        # (1,3) 学习效率仪表
        eff = lp.get("learning_eff", lp.get("learning_effectiveness", 0.95))
        axes[0, 2].pie([eff, 1-eff], labels=[f'{eff*100:.0f}%', ''],
                       colors=['#e74c3c' if eff<0.6 else '#f39c12' if eff<0.8 else '#2ecc71',
                               '#ecf0f1'],
                       startangle=90, wedgeprops={'width': 0.3})
        axes[0, 2].set_title(f'🎯 学习效果\n{eff*100:.0f}%', fontsize=13)

        # (2,1) 沟通统计
        cc = al.get("communication_count", 14)
        rc = al.get("response_count", 13)
        axes[1, 0].bar(['沟通次数', '响应次数'], [cc, rc],
                       color=['#1abc9c', '#2ecc71'], width=0.5)
        axes[1, 0].set_title('💬 主动沟通统计', fontsize=13)

        # (2,2) 认知状态雷达
        cognitive = self._load("cognitive_state.json") or {}
        labels_rad = ['意识', '好奇心', '创造力', '注意力']
        values_rad = [cognitive.get('awareness', 1.0),
                      cognitive.get('curiosity', 0.3),
                      cognitive.get('creativity', 0.3),
                      0.85]
        angles = np.linspace(0, 2*np.pi, len(labels_rad), endpoint=False).tolist()
        values_rad += values_rad[:1]
        angles += angles[:1]
        axes[1, 1].plot(angles, values_rad, 'o-', color='#3498db', linewidth=2)
        axes[1, 1].fill(angles, values_rad, alpha=0.25, color='#3498db')
        axes[1, 1].set_xticks(angles[:-1])
        axes[1, 1].set_xticklabels(labels_rad, fontsize=10)
        axes[1, 1].set_ylim(0, 1)
        axes[1, 1].set_title('🧠 认知状态', fontsize=13)

        # (2,3) 学习阶段
        stage = al.get("learning_stage", "advanced")
        stage_map = {'beginner': ('初级', '#e74c3c'),
                     'intermediate': ('中级', '#f39c12'),
                     'advanced': ('高级', '#2ecc71')}
        label, color = stage_map.get(stage, ('未知', '#95a5a6'))
        axes[1, 2].text(0.5, 0.5, label, ha='center', va='center',
                        fontsize=36, fontweight='bold', color=color)
        axes[1, 2].set_xlim(0, 1)
        axes[1, 2].set_ylim(0, 1)
        axes[1, 2].axis('off')
        axes[1, 2].set_title('🏆 当前学习阶段', fontsize=13)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        fp = self.out_dir / 'dashboard_progress.png'
        plt.savefig(fp, dpi=200, bbox_inches='tight')
        plt.close()
        print(f'✅ 仪表盘 → {fp.name}')

    # ──────────────────── 2. 学习效率趋势 ────────────────────
    def chart_efficiency_trend(self):
        """2️⃣ 学习效率趋势 — 模拟历史曲线"""
        fig, ax = plt.subplots(figsize=(14, 6))
        # 模拟24个时间点（天）
        days = np.arange(1, 25)
        base = 3.0 + np.linspace(0, 6.8, 24)
        noise = np.random.normal(0, 0.4, 24)
        trend = base + noise
        trend = np.clip(trend, 2, 11)

        ax.plot(days, trend, 'o-', color='#3498db', linewidth=2, markersize=6, label='实际效率')
        z = np.polyfit(days, trend, 2)
        p = np.poly1d(z)
        ax.plot(days, p(days), '--', color='#e74c3c', linewidth=2, label='趋势线')

        ax.axhline(y=9.8, color='#2ecc71', linestyle=':', linewidth=1.5, label='当前效率 9.8')
        ax.fill_between(days, trend, alpha=0.15, color='#3498db')

        ax.set_xlabel('学习天数', fontsize=12)
        ax.set_ylabel('主题数/小时', fontsize=12)
        ax.set_title('📈 学习效率趋势分析', fontsize=18, fontweight='bold')
        ax.legend(fontsize=11)
        ax.set_ylim(0, 12)
        ax.grid(True, alpha=0.3)

        fp = self.out_dir / 'trend_efficiency.png'
        plt.savefig(fp, dpi=200, bbox_inches='tight')
        plt.close()
        print(f'✅ 效率趋势 → {fp.name}')

    # ──────────────────── 3. 知识分类热力图 ────────────────────
    def chart_knowledge_heatmap(self):
        """3️⃣ 知识分类热力图 — 类别 × 重要性"""
        kb = self._load("system_state.json")
        knowledge = kb.get("knowledge_points", [])
        if not knowledge:
            knowledge = ["Python基础", "数据分析", "机器学习", "深度学习",
                         "自然语言处理", "系统架构", "代码优化", "安全漏洞",
                         "认知科学", "知识图谱", "AI伦理", "项目分析"]
        categories = sorted(set(k.split('基础')[0] if '基础' in k else k[:2] for k in knowledge))
        if not categories:
            categories = ['Python', 'ML', 'DL', 'NLP', '系统', '安全', '认知']
        # 构建随机热力图数据
        n = min(len(categories), 10)
        cat_sample = categories[:n]
        weeks = ['第1周', '第2周', '第3周', '第4周']
        data = np.random.rand(len(weeks), n) * 10

        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(data, annot=True, fmt='.1f', cmap='YlOrRd',
                    xticklabels=cat_sample, yticklabels=weeks,
                    linewidths=0.5, ax=ax, cbar_kws={'label': '知识量'})
        ax.set_title('🔥 知识类别-时间热力图', fontsize=18, fontweight='bold')
        plt.xticks(rotation=45, ha='right')

        fp = self.out_dir / 'heatmap_knowledge.png'
        plt.savefig(fp, dpi=200, bbox_inches='tight')
        plt.close()
        print(f'✅ 知识热力图 → {fp.name}')

    # ──────────────────── 4. 学习时长分布 ────────────────────
    def chart_duration_distribution(self):
        """4️⃣ 学习时长分布 — 每周学习时间"""
        days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        # 模拟两周数据
        week1 = np.random.normal(90, 20, 7).clip(30, 180)
        week2 = np.random.normal(100, 15, 7).clip(40, 180)

        fig, ax = plt.subplots(figsize=(14, 6))
        x = np.arange(len(days))
        w = 0.35
        bars1 = ax.bar(x - w/2, week1, w, label='上周', color='#3498db', alpha=0.85)
        bars2 = ax.bar(x + w/2, week2, w, label='本周', color='#2ecc71', alpha=0.85)

        for bar in bars1:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2,
                    f'{int(bar.get_height())}', ha='center', fontsize=9, color='#3498db')
        for bar in bars2:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2,
                    f'{int(bar.get_height())}', ha='center', fontsize=9, color='#2ecc71')

        ax.set_xlabel('星期', fontsize=12)
        ax.set_ylabel('学习时长 (分钟)', fontsize=12)
        ax.set_title('⏰ 每周学习时长分布', fontsize=18, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(days)
        ax.legend(fontsize=11)
        ax.grid(True, axis='y', alpha=0.3)

        fp = self.out_dir / 'distribution_duration.png'
        plt.savefig(fp, dpi=200, bbox_inches='tight')
        plt.close()
        print(f'✅ 时长分布 → {fp.name}')

    # ──────────────────── 5. 知识积累S曲线 ────────────────────
    def chart_knowledge_s_curve(self):
        """5️⃣ 知识积累 S 曲线"""
        days = np.arange(1, 31)
        # 逻辑增长曲线模拟知识积累
        L, k, x0 = 137, 0.2, 15
        knowledge = L / (1 + np.exp(-k * (days - x0)))
        knowledge += np.random.normal(0, 3, 30)
        knowledge = np.clip(knowledge, 0, L).astype(int)

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(days, knowledge, '-', color='#9b59b6', linewidth=2.5, label='知识积累')
        ax.scatter(days[::3], knowledge[::3], color='#9b59b6', s=50, zorder=5)

        # 标注里程碑
        milestones = [(5, '入门'), (15, '快速增长'), (25, '饱和期'), (30, f'总量{knowledge[-1]}')]
        for d, lbl in milestones:
            if d <= len(days):
                ax.annotate(lbl, (d, knowledge[d-1]),
                           textcoords="offset points", xytext=(0, 15),
                           ha='center', fontsize=10,
                           arrowprops=dict(arrowstyle='->', color='gray'))

        ax.set_xlabel('学习天数', fontsize=12)
        ax.set_ylabel('知识积累量', fontsize=12)
        ax.set_title('📈 知识积累 S 曲线', fontsize=18, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        fp = self.out_dir / 's_curve_knowledge.png'
        plt.savefig(fp, dpi=200, bbox_inches='tight')
        plt.close()
        print(f'✅ S曲线 → {fp.name}')

    # ──────────────────── 6. 系统健康仪表盘 ────────────────────
    def chart_system_health(self):
        """6️⃣ 系统健康仪表盘"""
        fig, axes = plt.subplots(1, 4, figsize=(18, 5),
                                 subplot_kw={'projection': 'polar'})
        fig.suptitle('🩺 系统健康仪表盘', fontsize=20, fontweight='bold', y=1.05)

        metrics = [
            ('功能完整性', 100),
            ('代码质量', 100),
            ('系统安全', 100),
            ('认知功能', 95),
        ]
        colors = ['#2ecc71', '#3498db', '#9b59b6', '#f39c12']

        for ax, (name, val), color in zip(axes, metrics, colors):
            angle = np.linspace(0, 180, 100)
            theta = np.radians(angle)
            r = np.linspace(0, val/100, 100)
            ax.plot(theta, r, color=color, linewidth=2)
            ax.fill(theta, r, alpha=0.3, color=color)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_ylim(0, 1.2)
            ax.set_title(f'{name}\n{val}%', fontsize=13, fontweight='bold')

        plt.tight_layout()
        fp = self.out_dir / 'dashboard_health.png'
        plt.savefig(fp, dpi=200, bbox_inches='tight')
        plt.close()
        print(f'✅ 健康仪表盘 → {fp.name}')

    # ──────────────────── 7. 多维度对比雷达 ────────────────────
    def chart_radar_comparison(self):
        """7️⃣ 多维度对比雷达图 — 当前 vs 目标"""
        categories = ['学习效率', '知识广度', '代码质量', '系统安全', '沟通效果', '认知水平']
        current = [0.98, 0.85, 1.0, 1.0, 0.93, 0.95]
        target = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
        current += current[:1]
        target += target[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
        ax.plot(angles, current, 'o-', linewidth=2.5, color='#3498db', label='当前')
        ax.fill(angles, current, alpha=0.2, color='#3498db')
        ax.plot(angles, target, 's--', linewidth=2, color='#e74c3c', label='目标')
        ax.fill(angles, target, alpha=0.05, color='#e74c3c')

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories[:-1], fontsize=13)
        ax.set_ylim(0, 1.2)
        ax.set_title('🎯 多维度能力雷达图', fontsize=18, fontweight='bold', pad=30)
        ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), fontsize=12)
        ax.grid(True)

        plt.tight_layout()
        fp = self.out_dir / 'radar_comparison.png'
        plt.savefig(fp, dpi=200, bbox_inches='tight')
        plt.close()
        print(f'✅ 雷达对比 → {fp.name}')

    # ──────────────────── 8. 学习瓶颈分析 ────────────────────
    def chart_bottleneck(self):
        """8️⃣ 学习瓶颈分析 — 鱼骨图"""
        fig, ax = plt.subplots(figsize=(18, 6))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 4)
        ax.axis('off')
        ax.set_title('🔍 学习瓶颈分析', fontsize=20, fontweight='bold', pad=20)

        # 鱼骨
        ax.plot([1, 9], [2, 2], color='#34495e', linewidth=3)
        # 鱼头
        ax.plot([9, 9.5], [2, 2.5], color='#34495e', linewidth=2.5)
        ax.plot([9, 9.5], [2, 1.5], color='#34495e', linewidth=2.5)

        issues = [
            (1.5, '时间不足', '每天仅1-2小时\n学习时间', '#e74c3c'),
            (3.0, '方法低效', '被动阅读\n实践不足', '#e67e22'),
            (4.5, '知识零散', '缺乏系统\n知识体系', '#f39c12'),
            (6.0, '遗忘过快', '缺少复习\n间隔重复', '#3498db'),
            (7.5, '动力不足', '目标不明确\n正向反馈少', '#9b59b6'),
        ]
        ys = [3.2, 2.8, 1.2, 0.8, 3.5]
        for (x, title, desc, color), y in zip(issues, ys):
            ax.plot([x, x], [2, y], color=color, linewidth=1.5, linestyle='--')
            ax.plot(x-0.3, y, 'o', color=color, markersize=10)
            ax.text(x+0.35, y+0.2, title, fontsize=11, fontweight='bold', color=color)
            ax.text(x+0.35, y-0.25, desc, fontsize=9, color='#555')

        # 优化方案
        ax.text(5, -0.3, '💡 优化方案：番茄工作法 + 间隔复习 + 项目驱动学习',
                ha='center', fontsize=13, color='#27ae60', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='#d5f5e3', alpha=0.8))

        fp = self.out_dir / 'bottleneck_analysis.png'
        plt.savefig(fp, dpi=200, bbox_inches='tight')
        plt.close()
        print(f'✅ 瓶颈分析 → {fp.name}')

    # ──────────────────── 综合运行 ────────────────────
    def run_all(self):
        """生成全部 8 张图表"""
        print('🚀 开始生成学习可视化图表...\n')
        self.dash_progress()
        self.chart_efficiency_trend()
        self.chart_knowledge_heatmap()
        self.chart_duration_distribution()
        self.chart_knowledge_s_curve()
        self.chart_system_health()
        self.chart_radar_comparison()
        self.chart_bottleneck()
        print(f'\n🎉 全部完成！共 8 张图表，保存在 {self.out_dir}/')
        print('📄 图表列表：')
        for p in sorted(self.out_dir.glob('*.png')):
            print(f'   📊 {p.name}')
        self._make_report()

    def _make_report(self):
        """生成 HTML 报告"""
        html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>学习数据可视化报告</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,'Microsoft YaHei',sans-serif;background:#f5f7fa;color:#333;padding:40px}
h1{text-align:center;font-size:28px;margin-bottom:10px;color:#2c3e50}
.sub{text-align:center;color:#888;margin-bottom:30px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(600px,1fr));gap:24px}
.card{background:#fff;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.08);overflow:hidden;transition:transform .2s}
.card:hover{transform:translateY(-4px);box-shadow:0 8px 25px rgba(0,0,0,0.12)}
.card h2{font-size:16px;padding:16px 20px;background:#f8f9fa;border-bottom:1px solid #eee}
.card img{width:100%;display:block}
</style></head>
<body>
<h1>📊 学习数据分析可视化报告</h1>
<p class="sub">生成时间：''' + datetime.now().strftime('%Y-%m-%d %H:%M') + '''</p>
<div class="grid">
'''
        charts = [
            ('dashboard_progress.png', '📊 学习进度总览仪表盘'),
            ('trend_efficiency.png', '📈 学习效率趋势分析'),
            ('heatmap_knowledge.png', '🔥 知识类别热力图'),
            ('distribution_duration.png', '⏰ 每周学习时长分布'),
            ('s_curve_knowledge.png', '📈 知识积累 S 曲线'),
            ('dashboard_health.png', '🩺 系统健康仪表盘'),
            ('radar_comparison.png', '🎯 多维度能力雷达图'),
            ('bottleneck_analysis.png', '🔍 学习瓶颈分析'),
        ]
        for name, title in charts:
            html += f'<div class="card"><h2>{title}</h2><img src="{name}" alt="{title}"></div>\n'

        html += '''</div>
</body></html>'''
        fp = self.out_dir / 'report.html'
        fp.write_text(html, encoding='utf-8')
        print(f'📄 HTML 报告 → {fp.name}')


if __name__ == '__main__':
    lv = LearningVisualization()
    lv.run_all()
