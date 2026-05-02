#!/usr/bin/env python3
"""
🎯 超级AI主动沟通系统
专注于真正的主动智能沟通能力
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from utils import measure_performance
from system_state_manager import SystemStateManager

class ActiveCommunicationAI:
    """主动沟通的AI系统 - 使用统一系统状态管理"""

    def __init__(self):
        """初始化"""
        print("🎯 初始化主动沟通系统")
        self.state_manager = SystemStateManager()
        self.data_dir = Path("data")
        self._init_system()
        print("✅ 主动沟通系统初始化完成")

    def _init_system(self):
        """初始化系统（使用统一状态管理）"""
        self.data_dir.mkdir(exist_ok=True)

        self.conversation_file = self.data_dir / "conversations.jsonl"
        if not self.conversation_file.exists():
            self.conversation_file.touch()

    def analyze_learning_state(self):
        """分析学习状态（使用统一状态管理）"""
        try:
            state = self.state_manager.get_state("active")

            stage = "beginner"
            if state["projects_completed"] >= 10:
                stage = "advanced"
            elif state["projects_completed"] >= 5:
                stage = "intermediate"

            state["learning_stage"] = stage
            self.state_manager.update_state("active", state)

            return state
        except Exception:
            return {
                "last_interaction": datetime.now().isoformat(),
                "learning_stage": "beginner",
                "projects_completed": 0,
                "communication_count": 0,
                "response_count": 0,
                "last_suggestion": "Python数据分析项目",
                "current_goal": "每天学习至少10个项目"
            }

    @measure_performance
    def decide_to_communicate(self):
        """决定是否应该主动沟通"""
        state = self.analyze_learning_state()
        time_since_last = self._time_since_last_interaction()

        # 1. 主动发现学习机会的触发条件
        if self._has_learning_opportunity():
            print("🔍 发现学习机会，准备主动沟通")
            return True

        # 2. 学习效果触发（效果不佳或特别优秀）
        if self._should_communicate_about_effectiveness():
            print("📈 学习效果分析，准备主动沟通")
            return True

        # 3. 新内容发现触发
        if self._has_new_content_to_share():
            print("✨ 发现新学习内容，准备主动沟通")
            return True

        # 4. 常规沟通触发
        if self._should_have_regular_check_in():
            print("⏰ 常规沟通时间，准备主动沟通")
            return True

        return False

    def _has_learning_opportunity(self):
        """判断是否有学习机会"""
        try:
            from self_learning_system import SelfLearningSystem
            from knowledge_base import KnowledgeBase

            # 检查知识库是否有新的高质量学习内容
            knowledge_base = KnowledgeBase()

            # 检查是否有重要性高的知识未学习
            results = knowledge_base.retrieve_knowledge(query="机器学习")
            if results and any(item.get("importance", 0) > 8 for item in results):
                return True

            # 检查学习系统是否发现新的学习策略
            learning_system = SelfLearningSystem()
            suggestions = learning_system.optimize_learning_strategy()
            if len(suggestions) > 3:
                return True

            return False

        except Exception as e:
            print(f"⚠️  学习机会检测失败: {e}")
            return False

    def _should_communicate_about_effectiveness(self):
        """判断是否需要沟通学习效果"""
        try:
            # 使用系统状态管理器获取学习状态
            learning = self.state_manager.get_state("learning")

            # 学习效果不佳（<0.7）或特别优秀（>0.9）
            if learning["learning_effectiveness"] < 0.7 or learning["learning_effectiveness"] > 0.9:
                return True

            # 学习效率发生显著变化（>20%差异）
            if len(learning["projects_studied"]) > 5:
                # 这里可以添加学习效率变化检测逻辑
                return False

            return False

        except Exception as e:
            print(f"⚠️  学习效果分析失败: {e}")
            return False

    def _has_new_content_to_share(self):
        """判断是否有新内容可以分享"""
        try:
            from browser_integration import BrowserIntegration

            # 检查浏览器是否有学习相关的内容
            browser_integration = BrowserIntegration()
            content_analysis = browser_integration.analyze_browser_content()

            if len(content_analysis) > 0:
                print(f"发现 {len(content_analysis)} 个学习相关内容")
                return True

            return False

        except Exception as e:
            print(f"⚠️  内容分析失败: {e}")
            return False

    def _should_have_regular_check_in(self):
        """判断是否需要常规沟通"""
        time_since_last = self._time_since_last_interaction()

        # 超过2小时没有沟通
        if time_since_last > 7200:
            return True

        return False

    def _time_since_last_interaction(self):
        """计算自上次交互以来的时间"""
        try:
            state = self.state_manager.get_state("active")
            last_time = datetime.fromisoformat(state["last_interaction"])
            return (datetime.now() - last_time).total_seconds()
        except Exception:
            return 3600

    def _update_state(self, state):
        """更新状态"""
        self.state_manager.update_state("active", state)

    def communicate_proactively(self):
        """主动沟通 - 发现好的东西然后主动沟通需不需要"""
        print("🤖 主动沟通...")

        # 分析当前状态
        state = self.analyze_learning_state()

        # 情感识别和关系管理
        emotion = self._recognize_emotion()
        relationship_score = self._assess_relationship()

        conversation = []
        conversation.append("晚上好！")

        # 根据情感状态调整问候语
        if emotion == "positive":
            conversation.append("我看到您的学习状态很好，继续保持！")
        elif emotion == "neutral":
            conversation.append("您看起来状态不错，今天有什么学习计划吗？")
        elif emotion == "negative":
            conversation.append("我注意到您可能需要一些鼓励，让我们一起克服困难！")

        # 发现并沟通学习机会
        if self._has_learning_opportunity():
            self._communicate_learning_opportunity(conversation, state)

        # 沟通学习效果
        if self._should_communicate_about_effectiveness():
            self._communicate_learning_effectiveness(conversation, state)

        # 分享新内容
        if self._has_new_content_to_share():
            self._communicate_new_content(conversation, state)

        # 常规沟通
        if len(conversation) <= 1:  # 只有默认问候语，没有新内容
            if state["learning_stage"] == "beginner":
                conversation.append("我注意到您还没有开始项目学习。")
                conversation.append("建议您先从基础项目开始，比如Python数据分析。")
                state["last_suggestion"] = "Python数据分析项目"
            elif state["learning_stage"] == "intermediate":
                conversation.append(f"您已经完成了 {state['projects_completed']} 个项目，学习进度不错！")
                conversation.append("我建议您继续学习机器学习项目，这会帮助您全面了解AI领域。")
                state["last_suggestion"] = "机器学习项目"
            else:
                conversation.append(f"您的学习进度很好，已完成 {state['projects_completed']} 个项目！")
                conversation.append("我建议您深入研究Trinity Claw的自我分析架构，这会增强您的主动智能能力。")
                state["last_suggestion"] = "Trinity Claw项目架构"

        # 提供学习进度分析
        learning = self.state_manager.get_state("learning")

        conversation.append(f"您当前的目标是：{state['current_goal']}")
        conversation.append(f"您已经学习了 {learning['total_study_time']} 分钟，掌握了 {len(learning['knowledge_points'])} 个知识要点。")

        # 根据学习效果提供建议
        if learning["learning_effectiveness"] < 0.8:
            conversation.append("我注意到您的学习效果还有提升空间，建议您调整学习方法。")
        elif learning["learning_effectiveness"] > 0.9:
            conversation.append("您的学习效果非常好，建议您继续保持当前的学习节奏。")

        # 根据关系评分调整沟通策略
        if relationship_score > 0.8:
            conversation.append("我们已经有了很好的学习伙伴关系，继续加油！")
        elif relationship_score > 0.5:
            conversation.append("我们正在建立良好的学习伙伴关系，共同进步！")
        else:
            conversation.append("让我们开始建立学习伙伴关系，一起成长！")

        conversation.append("您希望我继续处理什么任务？")

        for line in conversation:
            print(f"🤖 {line}")

        state["communication_count"] += 1
        state["last_interaction"] = datetime.now().isoformat()
        self._update_state(state)

        return conversation

    def _recognize_emotion(self):
        """情感识别"""
        # 简单的情感识别逻辑，可根据用户交互历史和学习进度判断
        try:
            learning = self.state_manager.get_state("learning")

            # 根据学习效率和任务完成情况判断情感
            if learning["learning_effectiveness"] > 0.9 and len(learning["projects_studied"]) > 0:
                return "positive"
            elif 0.6 < learning["learning_effectiveness"] <= 0.9:
                return "neutral"
            else:
                return "negative"
        except Exception:
            return "neutral"

    def _communicate_learning_opportunity(self, conversation, state):
        """沟通学习机会"""
        conversation.append("🎉 我发现了一些很好的学习机会！")

        try:
            from knowledge_base import KnowledgeBase
            knowledge_base = KnowledgeBase()

            # 查找重要性高的知识
            results = knowledge_base.retrieve_knowledge(query="机器学习")
            important_topics = [item for item in results if item.get("importance", 0) > 8]

            if important_topics:
                conversation.append(f"我发现了 {len(important_topics)} 个重要性很高的机器学习主题：")
                for i, topic in enumerate(important_topics[:2], 1):
                    conversation.append(f"   {i}. {topic['title']} - 重要性: {topic.get('importance', 0)}/10")

                conversation.append("您需要我详细介绍这些学习机会吗？")
                state["last_suggestion"] = important_topics[0]['title'] if important_topics else "机器学习"

        except Exception as e:
            print(f"⚠️  学习机会沟通失败: {e}")

    def _communicate_learning_effectiveness(self, conversation, state):
        """沟通学习效果"""
        try:
            learning = self.state_manager.get_state("learning")

            conversation.append("📊 您的学习效果分析：")
            conversation.append(f"   学习效果: {learning['learning_effectiveness']:.0%}")

            if learning["learning_effectiveness"] < 0.8:
                conversation.append("您的学习效果还有提升空间，建议调整学习策略。")
                conversation.append("我可以为您分析学习瓶颈并提供优化方案。")
            elif learning["learning_effectiveness"] > 0.9:
                conversation.append("您的学习效果非常优秀！建议挑战更难的主题。")
                conversation.append("我可以为您推荐进阶学习内容。")
            else:
                conversation.append("您的学习效果良好，保持这个节奏继续前进！")

        except Exception as e:
            print(f"⚠️  学习效果沟通失败: {e}")

    def _communicate_new_content(self, conversation, state):
        """沟通新发现的内容"""
        conversation.append("✨ 我发现了一些新的学习内容！")

        try:
            from browser_integration import BrowserIntegration
            browser_integration = BrowserIntegration()
            content_analysis = browser_integration.analyze_browser_content()

            if content_analysis:
                conversation.append(f"我在浏览器中发现了 {len(content_analysis)} 个学习相关内容：")

                for i, analysis in enumerate(content_analysis[:2], 1):
                    if analysis["analysis"].get("relevant"):
                        conversation.append(f"   {i}. {analysis['analysis']['title']}")
                        conversation.append(f"      相关性分析: {'非常相关' if analysis['analysis']['relevance'] > 0.8 else '相关'}")

                conversation.append("您需要我为您整理这些学习内容吗？")

        except Exception as e:
            print(f"⚠️  内容分析沟通失败: {e}")

    def _assess_relationship(self):
        """关系评估"""
        try:
            state = self.state_manager.get_state("active")

            # 根据沟通次数和响应次数计算关系评分
            if state["communication_count"] == 0:
                return 0.0

            return min(1.0, state["response_count"] / state["communication_count"])
        except Exception:
            return 0.0

    def process_user_response(self, user_input):
        """处理用户响应"""
        state = self.analyze_learning_state()
        print(f"🧑 用户响应: {user_input}")

        # 处理各种用户响应类型
        if user_input.lower() in ["继续", "好的", "是的", "开始", "学习", "项目", "任务"]:
            print("🤖 太好了！我立即为您准备学习任务。")
            self._execute_learning_task()
            state["response_count"] += 1
            state["projects_completed"] += 1
        elif user_input.lower() in ["休息", "稍后", "停止", "暂停", "退出"]:
            print("🤖 好的，您可以先休息一下。需要帮助时请随时告诉我。")
            state["response_count"] += 1
        elif user_input.lower() in ["状态", "进度", "统计", "查看"]:
            self._show_progress()
        elif user_input.lower() in ["建议", "指导", "帮助"]:
            self._provide_learning_suggestion()
        elif user_input.lower() in ["回顾", "总结", "报告"]:
            self._show_progress()
        elif user_input.lower() in ["目标", "计划", "规划"]:
            self._show_goal()
        else:
            print("🤖 我理解您的需求。让我为您准备相关内容。")
            self._execute_learning_task()

        state["last_interaction"] = datetime.now().isoformat()
        self._update_state(state)

        return True

    def _execute_learning_task(self):
        """执行学习任务"""
        state = self.analyze_learning_state()
        print(f"📋 正在执行学习任务: {state['last_suggestion']}")
        time.sleep(2)

        # 模拟任务执行
        print("✅ 学习任务完成！")

        # 记录学习进度
        self._record_learning_progress()

    def _record_learning_progress(self):
        """记录学习进度（使用统一状态管理）"""
        learning = self.state_manager.get_state("learning")
        state = self.analyze_learning_state()

        learning["total_study_time"] += 30  # 假设学习30分钟
        if state["last_suggestion"] not in learning["projects_studied"]:
            learning["projects_studied"].append(state["last_suggestion"])

        for p in ["项目分析技巧", "代码问题识别", "学习状态判断", "主动沟通方法"]:
            if p not in learning["knowledge_points"]:
                learning["knowledge_points"].append(p)

        learning["learning_effectiveness"] = min(1.0, learning["learning_effectiveness"] + 0.05)
        learning["communication_effectiveness"] = min(1.0, learning["communication_effectiveness"] + 0.03)

        self.state_manager.update_state("learning", learning)

        print("🎉 学习进度已记录！")

    def _show_progress(self):
        """显示学习进度"""
        state = self.analyze_learning_state()
        learning = self.state_manager.get_state("learning")

        print("\n📊 学习进度")
        print("=" * 60)
        print(f"🏆 完成项目: {state['projects_completed']}个")
        print(f"📚 已学项目: {len(learning['projects_studied'])}个")
        print(f"⏰ 学习时间: {learning['total_study_time']}分钟")
        print(f"💡 知识要点: {len(learning['knowledge_points'])}个")
        print(f"🎯 沟通次数: {state['communication_count']}次")
        print(f"💬 响应次数: {state['response_count']}次")
        print(f"📈 学习效率: {int(learning['learning_effectiveness'] * 100)}%")
        print(f"🔍 沟通效果: {int(learning['communication_effectiveness'] * 100)}%")
        print(f"🎯 学习阶段: {state['learning_stage']}")

    def _provide_learning_suggestion(self):
        """提供学习建议"""
        state = self.analyze_learning_state()
        learning = self.state_manager.get_state("learning")

        print("\n💡 学习建议")
        print("=" * 60)
        print(f"🏆 当前完成项目: {state['projects_completed']}个")
        print(f"📈 学习效率: {int(learning['learning_effectiveness'] * 100)}%")
        print(f"🎯 学习阶段: {state['learning_stage']}")

        # 根据学习阶段提供个性化建议
        if state["learning_stage"] == "beginner":
            print("建议您先从基础项目开始，比如Python数据分析。")
            print("重点学习：数据处理、数据分析基础、可视化")
        elif state["learning_stage"] == "intermediate":
            print("建议您继续学习机器学习项目，这会帮助您全面了解AI领域。")
            print("重点学习：机器学习算法、模型训练、评估")
        else:
            print("建议您深入研究Trinity Claw的自我分析架构，这会增强您的主动智能能力。")
            print("重点学习：架构设计、系统分析、自我优化")

    def _show_goal(self):
        """显示学习目标"""
        state = self.analyze_learning_state()

        print("\n🎯 学习目标")
        print("=" * 60)
        print(f"🏆 当前完成项目: {state['projects_completed']}个")
        learning = self.state_manager.get_state("learning")
        print(f"📚 已学项目: {len(learning['projects_studied'])}个")
        print(f"⏰ 学习时间: {learning['total_study_time']}分钟")
        print(f"🎯 当前目标: {state['current_goal']}")

    def run_communication_loop(self):
        """运行主动沟通循环"""
        print("🚀 主动沟通系统启动")
        print("=" * 60)

        while True:
            if self.decide_to_communicate():
                print()
                self.communicate_proactively()
                user_input = input("🧑 请输入您的响应: ").strip()
                if user_input.lower() in ["退出", "结束", "停止"]:
                    print("🎉 主动沟通系统已停止。")
                    break
                self.process_user_response(user_input)

            print("\n⏳ 等待下次沟通...")
            time.sleep(30)

    def quick_run(self):
        """快速运行"""
        print("🚀 快速沟通测试")
        print("=" * 60)

        self.analyze_learning_state()
        self.communicate_proactively()

        user_input = "继续"
        print(f"🧑 用户响应: {user_input}")
        self.process_user_response(user_input)


def main():
    """主函数"""
    ai = ActiveCommunicationAI()

    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        ai.run_communication_loop()
    else:
        ai.quick_run()


if __name__ == "__main__":
    main()