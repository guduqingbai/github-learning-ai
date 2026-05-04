#!/usr/bin/env python3
"""
🧠 认知架构模块 - 超级人工智能的理论基础实现
实现类似人类的认知结构和智能行为
架构一致性优化：使用统一系统状态管理
"""

import time
import random
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
from system_state_manager import SystemStateManager


class CognitiveArchitecture:
    """
    认知架构类 - 实现类似人类的认知结构
    使用统一系统状态管理
    """

    def __init__(self):
        """初始化认知架构"""
        print("🎯 初始化认知架构系统")

        # 统一系统状态管理
        self.state_manager = SystemStateManager()

        # 加载认知状态（使用统一状态管理）
        self._load_cognitive_state()

        # 知识库连接
        self.knowledge_base = None
        self._connect_knowledge_base()

        # 感知系统
        self.perception_system = PerceptionSystem()

        # 推理系统
        self.reasoning_system = ReasoningSystem()

        # 学习系统
        self.learning_system = LearningSystem()

        # 意图识别系统
        self.intention_recognition = None

        # 情感计算系统
        self.emotion_system = None

        print("✅ 认知架构系统初始化完成")

    def _load_cognitive_state(self):
        """加载认知状态（使用统一状态管理）"""
        try:
            cognitive_state = self.state_manager.get_state("cognitive")
            self.attention = cognitive_state.get("attention")
            self.focus = cognitive_state.get("focus")
            self.awareness = cognitive_state.get("awareness")
            self.curiosity = cognitive_state.get("curiosity")
            self.creativity = cognitive_state.get("creativity")

            print(f"🧠 认知状态加载成功: 注意力={self.attention}, 焦点={self.focus}, 意识={self.awareness:.1f}")

        except Exception as e:
            print(f"⚠️  认知状态加载失败: {e}")
            self._init_cognitive_state()

    def _init_cognitive_state(self):
        """初始化认知状态（使用统一状态管理）"""
        default_state = {
            "cognitive_id": str(uuid.uuid4()),
            "attention": None,
            "focus": None,
            "awareness": 0.5,
            "curiosity": 0.3,
            "creativity": 0.2,
            "learning_context": "正在学习机器学习",
            "last_perception": datetime.now().isoformat(),
            "last_reasoning": datetime.now().isoformat(),
            "last_learning": datetime.now().isoformat(),
            "last_intention": "学习机器学习",
            "emotional_state": "positive",
            "cognitive_load": 0.5,
            "energy_level": 0.8
        }

        self.state_manager.update_state("cognitive", default_state)
        self.attention = default_state["attention"]
        self.focus = default_state["focus"]
        self.awareness = default_state["awareness"]
        self.curiosity = default_state["curiosity"]
        self.creativity = default_state["creativity"]

        print("✅ 认知状态已初始化")

    def _save_cognitive_state(self):
        """保存认知状态（使用统一状态管理）"""
        state = self.state_manager.get_state("cognitive")
        state.update({
            "attention": self.attention,
            "focus": self.focus,
            "awareness": self.awareness,
            "curiosity": self.curiosity,
            "creativity": self.creativity,
            "last_perception": datetime.now().isoformat(),
            "last_reasoning": datetime.now().isoformat(),
            "last_learning": datetime.now().isoformat(),
        })
        self.state_manager.update_state("cognitive", state)
        print("📊 认知状态已保存")

    def _connect_knowledge_base(self):
        """连接知识库"""
        try:
            from knowledge_base import KnowledgeBase
            self.knowledge_base = KnowledgeBase()
        except Exception as e:
            print(f"⚠️  知识库连接失败: {e}")

    def perceive_environment(self):
        """感知环境 - 类似人类的感知系统"""
        try:
            # 感知学习数据
            perception_result = self.perception_system.perceive_learning_data()

            # 感知外部信息（浏览器、网络等）
            external_perception = self.perception_system.perceive_external_data()

            # 更新感知结果
            self.attention = perception_result.get("attention", None)
            self.focus = perception_result.get("focus", None)
            self.awareness = min(1.0, self.awareness + 0.1)

            print(f"🧠 感知系统: 注意力={self.attention}, 焦点={self.focus}, 意识={self.awareness:.1f}")

            return {
                "learning_perception": perception_result,
                "external_perception": external_perception
            }

        except Exception as e:
            print(f"⚠️  感知失败: {e}")
            return None

    def reason_about_situation(self, perception_data):
        """情境推理 - 类似人类的推理系统"""
        try:
            reasoning_result = self.reasoning_system.reason(perception_data)

            self.curiosity = reasoning_result.get("curiosity", self.curiosity)
            self.creativity = reasoning_result.get("creativity", self.creativity)

            print(f"🧠 推理系统: 好奇心={self.curiosity:.1f}, 创造力={self.creativity:.1f}")

            return reasoning_result

        except Exception as e:
            print(f"⚠️  推理失败: {e}")
            return None

    def decide_to_act(self, reasoning_result):
        """决策行动 - 类似人类的决策过程"""
        try:
            decision = self.reasoning_system.make_decision(reasoning_result)

            return decision

        except Exception as e:
            print(f"⚠️  决策失败: {e}")
            return None

    def learn_from_experience(self, decision, results):
        """从经验中学习 - 强化学习机制"""
        try:
            learning_result = self.learning_system.learn(decision, results)

            self._save_cognitive_state()

            return learning_result

        except Exception as e:
            print(f"⚠️  学习失败: {e}")
            return None

    def cognitive_cycle(self):
        """认知循环 - 完整的认知过程（可被思考守护进程周期性调用）"""
        print("🔄 开始认知循环...")

        # 1. 感知环境
        perception_data = self.perceive_environment()

        # 2. 情境推理
        reasoning_result = self.reason_about_situation(perception_data)

        # 3. 决策行动
        decision = self.decide_to_act(reasoning_result)

        # 4. 执行行动
        if decision:
            action_result = self._execute_action(decision)

            # 5. 学习经验
            self.learn_from_experience(decision, action_result)

        # 6. 根据认知状态调整思考频率
        self.adjust_thinking_frequency()

        print("✅ 认知循环完成")

    def adjust_thinking_frequency(self):
        """根据好奇心和创造力调整思考守护进程的频率"""
        try:
            from thinking_daemon import get_daemon
            daemon = get_daemon()

            # 好奇心高 → 思考更频繁（间隔缩短）
            # 好奇心低 → 思考更慢（间隔拉长）
            if self.curiosity > 0.7:
                new_interval = max(600, int(1800 * (1 - self.curiosity * 0.5)))
            elif self.curiosity > 0.4:
                new_interval = 1800
            else:
                new_interval = 3600

            if daemon.is_running and daemon.cycle_interval != new_interval:
                old = daemon.cycle_interval
                daemon.update_config(cycle_interval=new_interval)
                print(f"🧠 思考频率已调整: {old}秒 → {new_interval}秒 (好奇心={self.curiosity:.2f})")

        except Exception as e:
            print(f"⚠️  思考频率调整失败: {e}")

    def _execute_action(self, decision):
        """执行决策"""
        print(f"⚡ 执行决策: {decision}")

        # 如果决策是"探索新内容"，启动思考守护进程
        if "探索" in str(decision):
            try:
                from thinking_daemon import get_daemon
                daemon = get_daemon()
                if not daemon.is_running:
                    daemon.start()
                    print("🚀 已启动自主思考守护进程")
            except Exception as e:
                print(f"⚠️  启动思考守护进程失败: {e}")

        return {"success": True, "message": f"决策 '{decision}' 执行成功"}


class PerceptionSystem:
    """感知系统 - 类似人类的感知机制"""

    def perceive_learning_data(self):
        """感知学习数据"""
        try:
            from self_learning_system import SelfLearningSystem
            learning_system = SelfLearningSystem()

            learning_analysis = learning_system.analyze_learning_progress()
            learning_suggestions = learning_system.optimize_learning_strategy()

            # 评估学习数据的重要性
            importance_score = min(1.0, len(learning_suggestions) / 10)

            return {
                "attention": "学习进度",
                "focus": "机器学习",
                "importance": importance_score
            }

        except Exception as e:
            print(f"⚠️  学习数据感知失败: {e}")
            return None

    def perceive_external_data(self):
        """感知外部数据（浏览器、网络等）"""
        try:
            from browser_integration import BrowserIntegration
            browser_integration = BrowserIntegration()

            browser_data = browser_integration.collect_browser_data()

            return {
                "browser_content": browser_data
            }

        except Exception as e:
            print(f"⚠️  外部数据感知失败: {e}")
            return None


class ReasoningSystem:
    """推理系统 - 类似人类的推理机制"""

    def reason(self, perception_data):
        """情境推理（基于真实数据）"""
        # 从 CuriosityEngine 获取真实好奇心
        try:
            from self_scanner import SelfScanner
            from curiosity_engine import CuriosityEngine
            scanner = SelfScanner()
            snapshot = scanner.get_full_snapshot()
            engine = CuriosityEngine()
            questions = engine.generate_questions(snapshot)
            num_questions = len(questions)
        except Exception:
            num_questions = 0

        # 好奇心 = 有多少真实可探索的问题 / 最大预期
        max_expected = 12
        curiosity = min(1.0, num_questions / max_expected)

        # 创造力 = 项目自知识别比例（知道自己多少 = 能创造多少新连接）
        try:
            kb_data = snapshot.get("knowledge_base", {})
            cat_breakdown = kb_data.get("category_breakdown", {})
            self_entries = cat_breakdown.get("项目自身", 0)
            total_entries = kb_data.get("total_entries", 1)
            creativity = min(1.0, self_entries / max(1, total_entries) * 2)
        except Exception:
            creativity = 0.2

        # 知识图校准：用知识图缺口修正好奇心
        low_depth_count = 0
        try:
            from knowledge_graph import KnowledgeGraph
            kg = KnowledgeGraph()
            gaps = kg.find_gaps()
            low_depth_count = len([g for g in gaps if g['type'] == 'isolated'])
            if low_depth_count > 3:
                curiosity_boost = min(0.3, low_depth_count * 0.02)
                curiosity = min(1.0, curiosity + curiosity_boost)
        except Exception:
            pass

        reasoning_result = {
            "curiosity": curiosity,
            "creativity": creativity,
            "decision": None,
            "top_questions": [{"question": q.question} for q in questions[:3]]
            if num_questions > 0 else [],
            "low_depth_topics": low_depth_count,
        }

        # 感知数据修正
        if perception_data:
            learning_importance = perception_data.get("importance", 0)
            reasoning_result["curiosity"] = min(1.0, curiosity + learning_importance * 0.3)

        return reasoning_result

    def make_decision(self, reasoning_result):
        """决策制定"""
        if reasoning_result["curiosity"] > 0.6:
            return "探索新的学习内容"
        elif reasoning_result["curiosity"] > 0.4:
            return "深入学习当前主题"
        else:
            return "巩固已有知识"


class LearningSystem:
    """学习系统 - 类似人类的学习机制"""

    def learn(self, decision, results):
        """从经验中学习（调真实思考循环）"""
        try:
            from self_thinking_agent import SelfThinkingAgent
            agent = SelfThinkingAgent()
            insights = agent.run_thinking_cycle(depth=1)
            return {
                "learned": len(insights) > 0,
                "insights_generated": len(insights),
                "experience": f"决策 '{decision}' 执行，生成 {len(insights)} 个洞察",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "learned": True,
                "experience": f"决策 '{decision}' 执行",
                "timestamp": datetime.now().isoformat(),
                "note": str(e)
            }


def test_cognitive_architecture():
    """测试认知架构"""
    print("🎯 测试认知架构")
    print("=" * 50)

    try:
        cognitive_system = CognitiveArchitecture()

        print(f"🧠 认知架构初始化完成")

        # 测试认知循环
        for i in range(3):
            print(f"\n🔄 第 {i+1} 次认知循环:")
            cognitive_system.cognitive_cycle()
            time.sleep(1)

        print(f"\n✅ 认知架构测试完成")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    test_cognitive_architecture()
