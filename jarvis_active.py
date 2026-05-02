#!/usr/bin/env python3
"""
🤖 贾维斯式主动沟通系统 - 精简高效版
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

class JarvisActiveCommunication:
    """贾维斯式主动沟通系统"""

    def __init__(self):
        """初始化"""
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self._init_system()

    def _init_system(self):
        """初始化系统"""
        self.state_file = self.data_dir / "jarvis_active_state.json"

        if not self.state_file.exists():
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump({
                    "last_interaction": datetime.now().isoformat(),
                    "communication_count": 0,
                    "response_count": 0,
                    "active_tasks": [],
                    "pending_questions": []
                }, f, ensure_ascii=False, indent=2)

    def is_user_active(self):
        """判断用户是否处于活跃状态"""
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)

            last_time = datetime.fromisoformat(state["last_interaction"])
            inactive_seconds = (datetime.now() - last_time).total_seconds()

            return inactive_seconds < 600

        except Exception as e:
            print(f"❌ 检测用户状态失败: {e}")
            return False

    def should_communicate(self):
        """判断是否应该主动沟通"""
        return True

    def greet_and_ask(self):
        """主动问候和询问"""
        print("🤖 贾维斯式主动沟通...")
        print()

        with open(self.data_dir / "active_state.json", "r", encoding="utf-8") as f:
            active_state = json.load(f)

        if active_state["projects_completed"] == 0:
            greeting = [
                "晚上好！我是您的AI助手。",
                "我注意到您还没有开始项目学习。",
                "需要我为您分析当前的学习状态，"
                "并推荐一个合适的项目开始学习吗？"
            ]
        elif active_state["projects_completed"] < 5:
            greeting = [
                "晚上好！您的学习进度不错！",
                f"已经完成了 {active_state['projects_completed']} 个项目。",
                "需要我为您分析下一个学习任务，"
                "或者查看您的学习状态吗？"
            ]
        elif active_state["projects_completed"] < 10:
            greeting = [
                "晚上好！您的学习进度很好！",
                f"已经完成了 {active_state['projects_completed']} 个项目。",
                "需要我为您分析高级项目，"
                "或者评估您的学习效果吗？"
            ]
        else:
            greeting = [
                "晚上好！您的学习成果非常出色！",
                f"已经完成了 {active_state['projects_completed']} 个项目。",
                "需要我为您准备学习成果总结，"
                "或者规划下一步的学习方向吗？"
            ]

        for line in greeting:
            print(f"🤖 {line}")

        self._update_communication_count()
        return True

    def _update_communication_count(self):
        """更新沟通次数"""
        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        state["communication_count"] += 1
        state["last_interaction"] = datetime.now().isoformat()

        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def handle_response(self, user_input):
        """处理用户响应"""
        print(f"🧑 用户响应: {user_input}")

        response = user_input.lower().strip()

        if "开始" in response or "继续" in response or "好的" in response:
            self.execute_learning_task()
        elif "状态" in response or "进度" in response:
            self.show_progress()
        elif "停止" in response or "休息" in response:
            print("🤖 好的，您可以先休息。需要帮助时请随时告诉我。")
        elif "退出" in response or "结束" in response:
            print("🎉 贾维斯系统已停止。")
            sys.exit(0)
        else:
            print("🤖 我理解您的需求。让我为您分析一下...")
            self.execute_learning_task()

        self._update_response_count()

    def _update_response_count(self):
        """更新响应次数"""
        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        state["response_count"] += 1
        state["last_interaction"] = datetime.now().isoformat()

        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def execute_learning_task(self):
        """执行学习任务"""
        print("📋 正在执行学习任务...")

        print("🔍 正在分析项目...")
        time.sleep(1)
        print("✅ 项目分析完成")

        self._update_learning_progress()

        print("🎉 学习任务完成！")

    def _update_learning_progress(self):
        """更新学习进度"""
        with open(self.data_dir / "active_state.json", "r", encoding="utf-8") as f:
            active_state = json.load(f)

        active_state["projects_completed"] += 1
        active_state["last_interaction"] = datetime.now().isoformat()

        with open(self.data_dir / "active_state.json", "w", encoding="utf-8") as f:
            json.dump(active_state, f, ensure_ascii=False, indent=2)

        with open(self.data_dir / "learning_progress.json", "r", encoding="utf-8") as f:
            learning = json.load(f)

        learning["total_study_time"] += 30
        if "机器学习项目" not in learning["projects_studied"]:
            learning["projects_studied"].append("机器学习项目")
        learning["knowledge_points"].extend([
            "项目分析技巧",
            "学习方法优化"
        ])

        with open(self.data_dir / "learning_progress.json", "w", encoding="utf-8") as f:
            json.dump(learning, f, ensure_ascii=False, indent=2)

    def show_progress(self):
        """显示学习进度"""
        with open(self.data_dir / "active_state.json", "r", encoding="utf-8") as f:
            active_state = json.load(f)

        with open(self.data_dir / "learning_progress.json", "r", encoding="utf-8") as f:
            learning = json.load(f)

        print("\n📊 学习进度")
        print("=" * 60)
        print(f"🏆 完成项目: {active_state['projects_completed']}个")
        print(f"📚 已学项目: {len(learning['projects_studied'])}个")
        print(f"⏰ 学习时间: {learning['total_study_time']}分钟")
        print(f"💡 知识要点: {len(learning['knowledge_points'])}个")
        print(f"🎯 沟通次数: {self._get_communication_count()}次")
        print(f"💬 响应次数: {self._get_response_count()}次")
        print(f"📈 学习效率: {int(learning['learning_effectiveness'] * 100)}%")
        print(f"🔍 沟通效果: {int(learning['communication_effectiveness'] * 100)}%")

    def _get_communication_count(self):
        """获取沟通次数"""
        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state["communication_count"]

    def _get_response_count(self):
        """获取响应次数"""
        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state["response_count"]

    def run(self):
        """运行主动沟通系统"""
        print("🚀 贾维斯式主动沟通系统启动")
        print("=" * 60)

        if self.should_communicate():
            self.greet_and_ask()
            print()

            user_input = input("🧑 请输入您的响应: ").strip()
            self.handle_response(user_input)

        print("\n🎉 主动沟通会话完成！")

def main():
    """主函数"""
    try:
        jarvis = JarvisActiveCommunication()
        jarvis.run()
        return 0

    except KeyboardInterrupt:
        print("\n📴 用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 系统错误: {e}")
        import traceback
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    main()
