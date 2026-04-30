#!/usr/bin/env python3
"""
🎯 学习数据分析与优化系统Web界面
快速开发的Web界面，提供学习数据分析和优化功能
"""

import sys
import os
import json
import threading
import webbrowser
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入系统模块
from system_interfaces import get_system_interface

app = Flask(__name__)

# 全局系统接口实例
interface = get_system_interface()

# 基础HTML模板
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学习数据分析与优化系统</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .header h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-align: center;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        }
        .stat-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.2em;
            text-align: center;
        }
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #764ba2;
            text-align: center;
        }
        .stat-label {
            font-size: 0.9em;
            color: #666;
            text-align: center;
            margin-top: 5px;
        }
        .section {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .project-list {
            list-style: none;
            margin-top: 15px;
        }
        .project-list li {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            transition: background 0.3s ease;
        }
        .project-list li:hover {
            background: #e9ecef;
        }
        .button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 50px;
            font-size: 16px;
            cursor: pointer;
            margin: 5px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        .button:active {
            transform: translateY(0);
        }
        .button-group {
            text-align: center;
            margin-top: 20px;
        }
        .progress-bar {
            width: 100%;
            height: 25px;
            background: #f0f0f0;
            border-radius: 15px;
            overflow: hidden;
            margin: 15px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            transition: width 0.3s ease;
            border-radius: 15px 0 0 15px;
        }
        .progress-text {
            text-align: center;
            font-weight: bold;
            color: #666;
        }
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            .header h1 {
                font-size: 2em;
            }
            .stat-value {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 学习数据分析与优化系统</h1>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>学习项目</h3>
                <div class="stat-value">{{ projects_count }}</div>
                <div class="stat-label">已完成项目</div>
            </div>
            <div class="stat-card">
                <h3>学习要点</h3>
                <div class="stat-value">{{ knowledge_points }}</div>
                <div class="stat-label">已掌握要点</div>
            </div>
            <div class="stat-card">
                <h3>学习时间</h3>
                <div class="stat-value">{{ study_time }}</div>
                <div class="stat-label">学习时长 (分钟)</div>
            </div>
            <div class="stat-card">
                <h3>学习效果</h3>
                <div class="stat-value">{{ learning_effectiveness }}%</div>
                <div class="stat-label">学习效果评估</div>
            </div>
        </div>

        <div class="section">
            <h2>📊 学习进度</h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {{ progress_percentage }}%"></div>
            </div>
            <div class="progress-text">
                {{ progress_percentage }}% 完成 ({{ completed_projects }} / {{ total_projects }} 项目)
            </div>
        </div>

        <div class="section">
            <h2>📚 学习项目</h2>
            <ul class="project-list">
                {% for project in projects %}
                <li>
                    <strong>{{ project }}</strong>
                </li>
                {% endfor %}
            </ul>
        </div>

        <div class="section">
            <h2>🧠 认知状态</h2>
            <div style="text-align: center; font-size: 1.2em; margin-top: 15px;">
                <p>当前状态: {{ cognitive_state }}</p>
                <p>意识水平: {{ awareness }}%</p>
                <p>好奇心指数: {{ curiosity }}%</p>
            </div>
        </div>

        <div class="section">
            <h2>🎯 系统操作</h2>
            <div class="button-group">
                <button class="button" onclick="refreshData()">刷新数据</button>
                <button class="button" onclick="runLearningCycle()">开始学习</button>
                <button class="button" onclick="runSystemCheck()">系统检查</button>
                <button class="button" onclick="resetAllStates()">重置状态</button>
            </div>
        </div>
    </div>

    <script>
        function refreshData() {
            location.reload();
        }

        function runLearningCycle() {
            if (confirm('确定要开始新的学习周期吗？')) {
                fetch('/api/learning/start', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                })
                .catch(error => {
                    alert('开始学习周期失败: ' + error);
                });
            }
        }

        function runSystemCheck() {
            fetch('/api/system/check', {
                method: 'GET'
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                location.reload();
            })
            .catch(error => {
                alert('系统检查失败: ' + error);
            });
        }

        function resetAllStates() {
            if (confirm('确定要重置所有状态吗？这将清除所有学习数据！')) {
                fetch('/api/system/reset', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                })
                .catch(error => {
                    alert('重置状态失败: ' + error);
                });
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """首页"""
    # 获取系统状态
    learning_info = interface.learning.get_learning_info()
    cognitive_state = interface.cognitive.get_cognitive_state()

    # 计算学习进度
    completed_projects = len(learning_info.get('projects_studied', []))
    knowledge_points = len(learning_info.get('knowledge_points', []))
    study_time = int(learning_info.get('total_study_time', 0) / 60)  # 转换为分钟
    learning_effectiveness = int(learning_info.get('learning_effectiveness', 0) * 100)

    # 计算进度百分比
    total_projects = 10  # 假设目标是完成10个项目
    if completed_projects > total_projects:
        completed_projects = total_projects

    progress_percentage = int(completed_projects / total_projects * 100)

    # 渲染模板
    return render_template_string(BASE_TEMPLATE,
                               projects_count=completed_projects,
                               knowledge_points=knowledge_points,
                               study_time=study_time,
                               learning_effectiveness=learning_effectiveness,
                               progress_percentage=progress_percentage,
                               completed_projects=completed_projects,
                               total_projects=total_projects,
                               projects=learning_info.get('projects_studied', []),
                               cognitive_state=cognitive_state.get('attention', '学习'),
                               awareness=int(cognitive_state.get('awareness', 0) * 100),
                               curiosity=int(cognitive_state.get('curiosity', 0) * 100))

@app.route('/api/learning/start', methods=['POST'])
def start_learning():
    """开始学习周期"""
    try:
        from self_learning_system import SelfLearningSystem
        self_learning = SelfLearningSystem()
        self_learning.run_self_learning_cycle()
        return jsonify({'success': True, 'message': '学习周期已开始'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/system/check', methods=['GET'])
def system_check():
    """系统检查"""
    from system_self_check import SystemSelfCheck
    check = SystemSelfCheck()
    passed = check.run_full_check()

    if passed:
        return jsonify({'success': True, 'message': '系统检查通过'})
    else:
        return jsonify({'success': False, 'message': '系统检查未通过，请查看详细信息'})

@app.route('/api/system/reset', methods=['POST'])
def reset_system():
    """重置系统状态"""
    from system_state_manager import SystemStateManager
    state_manager = SystemStateManager()
    state_manager.reset_state()

    return jsonify({'success': True, 'message': '系统状态已重置'})

def run_web_interface(port=5000, debug=False):
    """运行Web界面"""
    print(f"🚀 学习数据分析与优化系统Web界面正在启动...")
    print(f"📡 访问地址: http://localhost:{port}")
    print(f"🎯 按 Ctrl+C 停止服务器")

    # 在浏览器中自动打开
    if not debug:
        webbrowser.open(f"http://localhost:{port}")

    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == "__main__":
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="学习数据分析与优化系统Web界面")
    parser.add_argument("-p", "--port", type=int, default=5000, help="服务器端口")
    parser.add_argument("-d", "--debug", action="store_true", help="启用调试模式")

    args = parser.parse_args()

    run_web_interface(args.port, args.debug)
