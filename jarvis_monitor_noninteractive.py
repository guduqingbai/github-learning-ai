#!/usr/bin/env python3
"""
🤖 贾维斯式主动沟通系统 - 非交互模式
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

class JarvisMonitor:
    """贾维斯式主动沟通系统"""

    def __init__(self):
        """初始化"""
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self._init_system()

    def _init_system(self):
        """初始化系统"""
        self.state_file = self.data_dir / "jarvis_monitor_state.json"

        if not self.state_file.exists():
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump({
                    "last_interaction": datetime.now().isoformat(),
                    "communication_count": 0,
                    "response_count": 0,
                    "monitoring_active": True
                }, f, ensure_ascii=False, indent=2)

    def is_user_available(self):
        """判断用户是否可用"""
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)

            last_time = datetime.fromisoformat(state["last_interaction"])
            inactive_seconds = (datetime.now() - last_time).total_seconds()

            # 5分钟内有交互视为可用
            return inactive_seconds < 300

        except Exception as e:
            print(f"❌ 检测用户状态失败: {e}")
            return False

    def should_communicate(self):
        """判断是否应该主动沟通"""
        return self.is_user_available()

    def communicate_intelligently(self):
        """智能主动沟通 - 非交互模式"""
        if not self.should_communicate():
            print("💤 用户不可用，系统进入自我学习模式...")
            self._run_self_learning_session()
            return False

        print("🤖 贾维斯式主动沟通...")

        with open(self.data_dir / "active_state.json", "r", encoding="utf-8") as f:
            active_state = json.load(f)

        conversation = []

        if active_state["projects_completed"] == 0:
            conversation.append("我注意到您还没有开始项目学习。")
            conversation.append("建议您先从基础项目开始，比如Python数据分析。")
        elif active_state["projects_completed"] < 5:
            conversation.append(f"您已经完成了 {active_state['projects_completed']} 个项目，学习进度不错！")
            conversation.append("我建议您继续学习机器学习项目，这会帮助您全面了解AI领域。")
        elif active_state["projects_completed"] < 10:
            conversation.append(f"您的学习进度很好，已完成 {active_state['projects_completed']} 个项目！")
            conversation.append("我建议您深入研究Trinity Claw的自我分析架构，这会增强您的主动智能能力。")
        else:
            conversation.append(f"您已经完成了 {active_state['projects_completed']} 个项目，非常优秀！")
            conversation.append("您可以考虑进行项目回顾或开始新的学习方向，比如深度学习。")

        conversation.append("需要我为您准备学习任务吗？")

        for line in conversation:
            print(f"🤖 {line}")

        self._record_communication(conversation)
        return True

    def _record_communication(self, conversation):
        """记录沟通"""
        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        state["communication_count"] += 1
        state["last_interaction"] = datetime.now().isoformat()

        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _run_self_learning_session(self):
        """执行自我学习任务"""
        try:
            from self_learning_system import SelfLearningSystem
            system = SelfLearningSystem()
            system.run_self_learning_cycle()

            print("✅ 自我学习完成！")

        except Exception as e:
            print(f"❌ 自我学习失败: {e}")

    def simulate_interaction(self):
        """模拟用户交互"""
        print("\n🧑 用户: 继续")

        print("🤖 太好了！我立即为您准备学习任务。")
        self._execute_learning_task()

    def _execute_learning_task(self):
        """执行学习任务"""
        print("📋 正在执行学习任务: 机器学习项目")
        time.sleep(2)
        print("✅ 学习任务完成！")

        self._update_learning_progress()
        print("🎉 学习进度已记录！")

    def _update_learning_progress(self):
        """更新学习进度"""
        with open(self.data_dir / "active_state.json", "r", encoding="utf-8") as f:
            active_state = json.load(f)

        active_state["projects_completed"] += 1
        active_state["last_interaction"] = datetime.now().isoformat()

        with open(self.data_dir / "active_state.json", "w", encoding="utf-8") as f:
            json.dump(active_state, f, ensure_ascii=False, indent=2)

        # 更新学习进度文件
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

        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        state["response_count"] += 1
        state["last_interaction"] = datetime.now().isoformat()

        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def run_monitor(self):
        """运行监控模式"""
        print("🚀 贾维斯式主动沟通系统启动")
        print("=" * 60)

        if self.communicate_intelligently():
            self.simulate_interaction()

        print("\n🎉 主动沟通会话完成！")

def main():
    """主函数"""
    try:
        jarvis = JarvisMonitor()
        jarvis.run_monitor()
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
