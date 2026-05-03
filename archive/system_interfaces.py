#!/usr/bin/env python3
"""
🎯 系统接口模块 - 架构一致性优化
提供统一的系统接口，确保各个模块之间的接口一致性
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from system_state_manager import SystemStateManager


class LearningInterface:
    """学习系统统一接口"""

    def __init__(self):
        self.state_manager = SystemStateManager()

    def get_learning_state(self) -> Dict[str, Any]:
        """获取学习状态"""
        return self.state_manager.get_state("learning")

    def get_learning_info(self) -> Dict[str, Any]:
        """获取学习信息（兼容Web界面）"""
        return self.get_learning_state()

    def update_learning_progress(self, time_seconds: float, knowledge_points: List[str] = None):
        """更新学习进度"""
        learning = self.get_learning_state()
        learning["total_study_time"] += time_seconds
        if knowledge_points:
            learning["knowledge_points"].extend(knowledge_points)
        self.state_manager.update_state("learning", learning)

    def add_project_studied(self, project_name: str):
        """添加已学习项目"""
        learning = self.get_learning_state()
        if project_name not in learning["projects_studied"]:
            learning["projects_studied"].append(project_name)
        self.state_manager.update_state("learning", learning)

    def get_learning_effectiveness(self) -> float:
        """获取学习效果"""
        return self.state_manager.get_state("learning", "learning_effectiveness")


class CommunicationInterface:
    """主动沟通系统统一接口"""

    def __init__(self):
        self.state_manager = SystemStateManager()

    def get_communication_state(self) -> Dict[str, Any]:
        """获取沟通状态"""
        return self.state_manager.get_state("active")

    def update_communication_state(self, state: Dict[str, Any]):
        """更新沟通状态"""
        self.state_manager.update_state("active", state)

    def record_interaction(self, user_input: str, ai_response: str):
        """记录交互"""
        active = self.get_communication_state()
        active["communication_count"] += 1
        active["response_count"] += 1
        active["last_interaction"] = datetime.now().isoformat()
        self.state_manager.update_state("active", active)

    def update_suggestion(self, suggestion: str):
        """更新建议"""
        self.state_manager.set_state("active", "last_suggestion", suggestion)

    def get_suggestion(self) -> str:
        """获取当前建议"""
        return self.state_manager.get_state("active", "last_suggestion")


class CognitiveInterface:
    """认知架构系统统一接口"""

    def __init__(self):
        self.state_manager = SystemStateManager()

    def get_cognitive_state(self) -> Dict[str, Any]:
        """获取认知状态"""
        return self.state_manager.get_state("cognitive")

    def update_cognitive_state(self, changes: Dict[str, Any]):
        """更新认知状态"""
        cognitive = self.get_cognitive_state()
        cognitive.update(changes)
        cognitive["last_perception"] = datetime.now().isoformat()
        self.state_manager.update_state("cognitive", cognitive)

    def get_attention(self) -> str:
        """获取注意力焦点"""
        return self.state_manager.get_state("cognitive", "attention")

    def get_awareness(self) -> float:
        """获取意识水平"""
        return self.state_manager.get_state("cognitive", "awareness")


class ContinuousLearningInterface:
    """持续学习系统统一接口"""

    def __init__(self):
        self.state_manager = SystemStateManager()

    def get_continuous_learning_state(self) -> Dict[str, Any]:
        """获取持续学习状态"""
        return self.state_manager.get_state("continuous")

    def update_learning_state(self, state: Dict[str, Any]):
        """更新持续学习状态"""
        self.state_manager.update_state("continuous", state)

    def update_learning_count(self, count: int = 1):
        """更新学习次数"""
        self.state_manager.update_state("continuous", {
            "learning_count": self.get_continuous_learning_state()["learning_count"] + count
        })

    def update_learning_duration(self, duration_seconds: float):
        """更新学习时长"""
        continuous = self.get_continuous_learning_state()
        continuous["learning_duration"] += duration_seconds / 60  # 转换为分钟
        self.state_manager.update_state("continuous", continuous)

class SelfLearningInterface:
    """自我学习系统统一接口"""

    def __init__(self):
        self.state_manager = SystemStateManager()

    def get_self_learning_state(self) -> Dict[str, Any]:
        """获取自我学习状态"""
        return self.state_manager.get_state("self_learning")

class JarvisInterface:
    """Jarvis系统统一接口"""

    def __init__(self):
        self.state_manager = SystemStateManager()

    def get_jarvis_state(self) -> Dict[str, Any]:
        """获取Jarvis系统状态"""
        return self.state_manager.get_state("jarvis")

    def update_jarvis_status(self, status: str):
        """更新Jarvis系统状态"""
        self.state_manager.set_state("jarvis", "status", status)

    def record_optimization(self):
        """记录优化"""
        system = self.state_manager.get_state("system")
        system["last_optimized"] = datetime.now().isoformat()
        self.state_manager.update_state("system", system)

    def get_performance_score(self) -> int:
        """获取性能分数"""
        return self.state_manager.get_state("system", "performance_score")


class GlobalSystemInterface:
    """全局系统统一接口"""

    def __init__(self):
        self.state_manager = SystemStateManager()
        self.learning = LearningInterface()
        self.communication = CommunicationInterface()
        self.cognitive = CognitiveInterface()
        self.continuous = ContinuousLearningInterface()
        self.self_learning = SelfLearningInterface()
        self.jarvis = JarvisInterface()

    def get_global_state_summary(self) -> Dict[str, Any]:
        """获取全局系统状态摘要"""
        learning = self.learning.get_learning_state()
        active = self.communication.get_communication_state()
        cognitive = self.cognitive.get_cognitive_state()

        return {
            "learning": {
                "total_time": learning["total_study_time"],
                "projects": len(learning["projects_studied"]),
                "knowledge_points": len(learning["knowledge_points"]),
                "effectiveness": learning["learning_effectiveness"]
            },
            "communication": {
                "count": active["communication_count"],
                "response_rate": active["response_count"] / active["communication_count"] if active["communication_count"] > 0 else 0,
                "stage": active["learning_stage"]
            },
            "cognitive": {
                "awareness": cognitive["awareness"],
                "curiosity": cognitive["curiosity"],
                "creativity": cognitive["creativity"]
            },
            "system": {
                "version": self.state_manager.get_state("system", "version"),
                "performance": self.state_manager.get_state("system", "performance_score")
            }
        }

    def reset_all_states(self):
        """重置所有状态"""
        for module_name in ["active", "cognitive", "continuous", "learning", "system"]:
            self.state_manager.reset_state(module_name)

    def save_system_snapshot(self, filename: str = None):
        """保存系统快照"""
        if filename is None:
            filename = f"system_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        snapshot = self.state_manager.get_global_state()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)

        return filename


# 全局接口实例（单例模式）
_global_interface = None


def get_system_interface() -> GlobalSystemInterface:
    """获取全局系统接口（单例模式）"""
    global _global_interface
    if _global_interface is None:
        _global_interface = GlobalSystemInterface()
    return _global_interface


def test_system_interfaces():
    """测试系统接口功能"""
    print("🎯 测试系统接口功能")
    print("=" * 60)

    try:
        interface = get_system_interface()

        # 测试学习系统接口
        print("\n📚 测试学习系统接口:")
        initial_points = interface.learning.get_learning_effectiveness()
        print(f"学习效果: {initial_points:.2f}")

        # 测试主动沟通系统接口
        print("\n💬 测试主动沟通系统接口:")
        current_suggestion = interface.communication.get_suggestion()
        print(f"当前建议: {current_suggestion}")

        # 测试认知架构系统接口
        print("\n🧠 测试认知架构系统接口:")
        cognitive = interface.cognitive.get_cognitive_state()
        print(f"认知状态: {len(cognitive)} 个字段")

        # 测试持续学习系统接口
        print("\n🔄 测试持续学习系统接口:")
        continuous = interface.continuous.get_continuous_learning_state()
        print(f"学习次数: {continuous['learning_count']}")

        # 测试全局系统接口
        print("\n🌐 测试全局系统接口:")
        summary = interface.get_global_state_summary()
        print(f"学习时间: {summary['learning']['total_time']} 秒")
        print(f"学习项目: {summary['learning']['projects']} 个")
        print(f"知识点数: {summary['learning']['knowledge_points']} 个")

        print("\n✅ 所有系统接口测试成功!")
        return True

    except Exception as e:
        print(f"\n❌ 系统接口测试失败: {e}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    test_system_interfaces()
