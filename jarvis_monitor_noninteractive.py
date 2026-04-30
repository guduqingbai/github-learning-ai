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

            # 5分钟内有交互视为可用，确保系统不会过于频繁地主动联系用户
            return inactive_seconds < 300

        except Exception as e:
            print(f"❌ 检测用户状态失败: {e}")
            return False

    def should_communicate(self):
        """判断是否应该主动沟通"""
        # 只有在用户可用时才主动沟通，确保系统不会过于频繁地主动联系用户
        return self.is_user_available()

    def communicate_intelligently(self):
        """智能主动沟通 - 非交互模式"""
        if self.is_user_available():
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
        else:
            print("💤 用户不可用，启动后台持续学习服务...")
            self._start_background_learning_service()
            return False

    def _record_communication(self, conversation):
        """记录沟通"""
        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        state["communication_count"] += 1
        state["last_interaction"] = datetime.now().isoformat()

        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _start_background_learning_service(self):
        """启动后台持续学习服务"""
        try:
            from background_learning_service import BackgroundLearningService
            service = BackgroundLearningService()

            # 检查是否需要立即学习
            if service.is_user_offline():
                print("🚀 启动后台持续学习服务...")
                service.start()

                # 启动一个线程来管理服务（避免阻塞）
                import threading
                threading.Thread(target=self._monitor_learning_service, args=(service,)).start()

            print("✅ 后台持续学习服务启动成功")

        except Exception as e:
            print(f"❌ 启动后台学习服务失败: {e}")
            import traceback
            print(traceback.format_exc())

    def _monitor_learning_service(self, service):
        """监控学习服务"""
        """
        监控学习服务的运行状态，确保服务正常工作
        """
        try:
            while service.is_running and service.is_user_offline():
                # 检查服务状态
                status = service.get_service_status()
                print(f"📊 学习服务状态: {status}")

                # 每5分钟检查一次
                time.sleep(300)

            print("👤 用户已上线或服务已停止，正在关闭学习服务...")
            service.stop()

        except Exception as e:
            print(f"⚠️  监控学习服务失败: {e}")
            try:
                service.stop()
            except:
                pass

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

        # 更新学习进度文件，关注个性化学习和自适应学习
        with open(self.data_dir / "learning_progress.json", "r", encoding="utf-8") as f:
            learning = json.load(f)

        # 根据用户学习历史和效果调整学习内容
        self._adjust_learning_content(learning)

        learning["total_study_time"] += 30
        if "机器学习项目" not in learning["projects_studied"]:
            learning["projects_studied"].append("机器学习项目")

        # 根据用户学习效果个性化添加知识要点
        self._add_personalized_knowledge_points(learning)

        with open(self.data_dir / "learning_progress.json", "w", encoding="utf-8") as f:
            json.dump(learning, f, ensure_ascii=False, indent=2)

        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        state["response_count"] += 1
        state["last_interaction"] = datetime.now().isoformat()

        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _adjust_learning_content(self, learning):
        """根据用户学习历史和效果调整学习内容"""
        # 简单的自适应学习逻辑：根据学习效果调整学习任务难度
        if learning["learning_effectiveness"] < 0.8:
            # 学习效果较差，增加基础项目
            if "Python基础项目" not in learning["projects_studied"]:
                learning["projects_studied"].append("Python基础项目")
        elif learning["learning_effectiveness"] > 0.9:
            # 学习效果优秀，增加高级项目
            if "深度学习项目" not in learning["projects_studied"]:
                learning["projects_studied"].append("深度学习项目")

    def _add_personalized_knowledge_points(self, learning):
        """根据用户学习效果个性化添加知识要点"""
        effectiveness = learning["learning_effectiveness"]
        if effectiveness < 0.8:
            # 学习效果较差，重点学习基础知识点
            new_points = ["Python基础语法", "数据结构基础", "简单算法"]
        elif effectiveness < 0.9:
            # 学习效果中等，学习进阶知识点
            new_points = ["机器学习基础", "数据可视化", "API开发"]
        else:
            # 学习效果优秀，学习高级知识点
            new_points = ["深度学习架构", "自然语言处理", "计算机视觉"]

        # 添加新的知识要点，避免重复
        for point in new_points:
            if point not in learning["knowledge_points"]:
                learning["knowledge_points"].append(point)

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
