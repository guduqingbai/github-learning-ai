#!/usr/bin/env python3
"""
🤖 贾维斯式智能主动沟通系统
实现钢铁侠中贾维斯那样的智能化有效沟通
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path

class JarvisCommunication:
    """贾维斯式智能沟通系统"""

    def __init__(self):
        """初始化"""
        self.data_dir = Path("data")
        self._init_system()

    def _init_system(self):
        """初始化系统"""
        self.data_dir.mkdir(exist_ok=True)

        self.state_file = self.data_dir / "jarvis_state.json"
        self.context_file = self.data_dir / "communication_context.json"
        self.knowledge_file = self.data_dir / "jarvis_knowledge.json"

        if not self.state_file.exists():
            self._reset_state()

        if not self.context_file.exists():
            with open(self.context_file, "w", encoding="utf-8") as f:
                json.dump({
                    "conversation_history": [],
                    "current_topic": None,
                    "last_question": None,
                    "user_preferences": {
                        "learning_style": "practical",
                        "response_length": "concise",
                        "communication_time": "flexible"
                    }
                }, f, ensure_ascii=False, indent=2)

        if not self.knowledge_file.exists():
            with open(self.knowledge_file, "w", encoding="utf-8") as f:
                json.dump({
                    "user_questions": [],
                    "learning_patterns": [],
                    "interaction_history": []
                }, f, ensure_ascii=False, indent=2)

    def _reset_state(self):
        """重置系统状态"""
        state = {
            "is_active": False,
            "user_status": "online",  # online, idle, away, offline
            "last_interaction": datetime.now().isoformat(),
            "last_communication": None,
            "active_tasks": [],
            "pending_questions": [],
            "communication_count": 0,
            "response_count": 0
        }

        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def detect_user_status(self):
        """检测用户状态"""
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)

            last_time = datetime.fromisoformat(state["last_interaction"])
            time_diff = (datetime.now() - last_time).total_seconds()

            if time_diff < 60:
                status = "online"
            elif time_diff < 300:
                status = "idle"
            elif time_diff < 3600:
                status = "away"
            else:
                status = "offline"

            state["user_status"] = status
            self._update_state(state)

            return status

        except Exception as e:
            print(f"❌ 检测用户状态失败: {e}")
            return "offline"

    def should_communicate(self):
        """判断是否应该主动沟通"""
        status = self.detect_user_status()

        if status in ["idle", "away"]:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)

            # 如果有未完成任务或待解决问题
            if state["active_tasks"] or state["pending_questions"]:
                return True

            # 如果用户之前有学习计划但暂停了
            with open(self.data_dir / "active_state.json", "r", encoding="utf-8") as f:
                active_state = json.load(f)

            if active_state["projects_completed"] < active_state.get("current_goal", 10):
                return True

        return False

    def communicate_intelligently(self):
        """智能主动沟通"""
        if not self.should_communicate():
            return False

        print("🤖 贾维斯式主动沟通...")

        status = self.detect_user_status()
        context = self._get_communication_context()

        conversation = []

        if status == "idle":
            conversation.append("先生，您看起来在思考。需要我为您分析一下当前的学习进度吗？")
        elif status == "away":
            conversation.append("先生，您已经有一段时间没有学习了。需要我为您准备下一个任务吗？")

        # 根据上下文提供个性化建议
        if context["current_topic"]:
            conversation.append(f"关于 {context['current_topic']}，我发现了一些新的学习资源。")

        conversation.append("需要我为您继续处理什么吗？")

        for line in conversation:
            print(f"🤖 {line}")

        self._record_communication(conversation)
        return True

    def _get_communication_context(self):
        """获取沟通上下文"""
        with open(self.context_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _record_communication(self, conversation):
        """记录沟通"""
        with open(self.context_file, "r", encoding="utf-8") as f:
            context = json.load(f)

        context["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "type": "system_initiated",
            "content": conversation,
            "context": {
                "user_status": self.detect_user_status()
            }
        })

        with open(self.context_file, "w", encoding="utf-8") as f:
            json.dump(context, f, ensure_ascii=False, indent=2)

        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        state["last_communication"] = datetime.now().isoformat()
        state["communication_count"] += 1
        self._update_state(state)

    def respond_naturally(self, user_input):
        """自然响应"""
        print(f"🧑 用户: {user_input}")

        response = self._generate_response(user_input)

        for line in response:
            print(f"🤖 {line}")

        self._update_user_status("online")
        return True

    def _generate_response(self, user_input):
        """生成响应"""
        lower_input = user_input.lower()

        if any(keyword in lower_input for keyword in ["学习", "项目", "任务"]):
            return self._handle_learning_request()
        elif any(keyword in lower_input for keyword in ["状态", "进度", "统计"]):
            return self._handle_status_request()
        elif any(keyword in lower_input for keyword in ["停止", "结束", "休息"]):
            return self._handle_stop_request()
        elif any(keyword in lower_input for keyword in ["帮助", "建议", "推荐"]):
            return self._handle_help_request()
        else:
            return self._handle_generic_request(user_input)

    def _handle_learning_request(self):
        """处理学习请求"""
        return [
            "很好，先生！我立即为您准备学习任务。",
            "根据您的学习进度，我建议学习机器学习项目。",
            "需要我立即开始分析项目吗？"
        ]

    def _handle_status_request(self):
        """处理状态请求"""
        try:
            with open(self.data_dir / "active_state.json", "r", encoding="utf-8") as f:
                active_state = json.load(f)

            with open(self.data_dir / "learning_progress.json", "r", encoding="utf-8") as f:
                learning = json.load(f)

            return [
                f"📊 学习进度: {active_state['projects_completed']}/{active_state['current_goal']}",
                f"⏰ 学习时间: {learning['total_study_time']}分钟",
                f"🎯 已学项目: {len(learning['projects_studied'])}个",
                f"💡 知识要点: {len(learning['knowledge_points'])}个"
            ]

        except Exception as e:
            return [f"⚠️ 获取学习状态失败: {e}"]

    def _handle_stop_request(self):
        """处理停止请求"""
        self._update_user_status("idle")
        return [
            "好的，先生。我保持待命状态。",
            "需要帮助时，请随时告诉我。"
        ]

    def _handle_help_request(self):
        """处理帮助请求"""
        return [
            "我可以帮助您以下任务：",
            "- 分析项目并提供学习建议",
            "- 记录和跟踪学习进度",
            "- 获取最新AI知识和行业动态",
            "- 回答编程和机器学习问题"
        ]

    def _handle_generic_request(self, input_text):
        """处理通用请求"""
        return [
            "我理解您的需求，先生。",
            "让我为您分析一下...",
            "需要我立即为您准备相关内容吗？"
        ]

    def _update_state(self, state):
        """更新状态"""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _update_user_status(self, status):
        """更新用户状态"""
        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        state["user_status"] = status
        state["last_interaction"] = datetime.now().isoformat()
        state["response_count"] += 1
        self._update_state(state)

    def run_jarvis_system(self):
        """运行贾维斯系统"""
        print("🚀 贾维斯式智能沟通系统启动")
        print("=" * 60)

        while True:
            status = self.detect_user_status()

            if status == "online":
                if self.should_communicate():
                    self.communicate_intelligently()
                    user_input = input("🧑 ").strip()

                    if user_input.lower() in ["退出", "结束"]:
                        print("🎉 贾维斯系统已停止。")
                        break

                    self.respond_naturally(user_input)

                else:
                    print("\n⏳ 贾维斯系统待命...")
                    time.sleep(60)

            elif status == "offline":
                print("\n💤 先生不在线，系统进入后台学习模式...")
                self._run_background_learning()
                time.sleep(3600)

            else:
                time.sleep(60)

    def _run_background_learning(self):
        """后台学习"""
        try:
            from self_learning_system import SelfLearningSystem
            system = SelfLearningSystem()

            print("📚 正在进行自我学习...")
            system.run_self_learning_cycle()

            print("✅ 自我学习完成！")

            # 记录学习成果到知识库
            self._record_learning_session()

        except Exception as e:
            print(f"❌ 后台学习失败: {e}")

    def _record_learning_session(self):
        """记录学习会话"""
        try:
            with open(self.knowledge_file, "r", encoding="utf-8") as f:
                knowledge = json.load(f)

            knowledge["learning_patterns"].append({
                "timestamp": datetime.now().isoformat(),
                "type": "self_learning",
                "duration": 3600,
                "topics": [
                    "项目分析",
                    "代码优化",
                    "AI最新进展",
                    "系统漏洞检查"
                ]
            })

            with open(self.knowledge_file, "w", encoding="utf-8") as f:
                json.dump(knowledge, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"❌ 记录学习成果失败: {e}")


def main():
    """主函数"""
    jarvis = JarvisCommunication()

    try:
        jarvis.run_jarvis_system()
        return 0
    except KeyboardInterrupt:
        print("\n📴 用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 系统错误: {e}")
        return 1


if __name__ == "__main__":
    main()