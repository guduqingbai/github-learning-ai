#!/usr/bin/env python3
"""
📊 统一系统状态管理模块 - 架构一致性优化
实现系统状态的统一管理和恢复机制
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from utils import measure_performance


class SystemStateManager:
    """
    统一系统状态管理类
    负责所有模块的状态数据管理和操作
    """

    # 类级别的单例实例
    _instance = None

    def __new__(cls):
        """单例模式实现，避免重复初始化"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化系统状态管理器（单例模式）"""
        if self._initialized:
            return

        self._initialized = True
        self.data_dir = Path("data")
        self._init_data_dir()

        # 状态文件映射
        self.state_config = {
            "active": {
                "file": "active_state.json",
                "default": self._get_active_state_defaults
            },
            "continuous": {
                "file": "continuous_learning_state.json",
                "default": self._get_continuous_state_defaults
            },
            "cognitive": {
                "file": "cognitive_state.json",
                "default": self._get_cognitive_state_defaults
            },
            "self_learning": {
                "file": "self_learning_records.json",
                "default": self._get_self_learning_state_defaults
            },
            "jarvis": {
                "file": "jarvis_state.json",
                "default": self._get_jarvis_state_defaults
            },
            "learning": {
                "file": "learning_progress.json",
                "default": self._get_learning_progress_defaults
            },
            "system": {
                "file": "system_state.json",
                "default": self._get_system_state_defaults
            },
            "knowledge": {
                "file": "knowledge_base.json",
                "default": self._get_knowledge_base_defaults
            },
            "vulnerabilities": {
                "file": "vulnerabilities.json",
                "default": self._get_vulnerabilities_defaults
            }
        }

        # 内存中的状态缓存
        self._state_cache: Dict[str, Dict[str, Any]] = {}
        # 状态加载标志，用于跟踪已加载的模块
        self._loaded_modules: set = set()
        # 状态访问统计，用于优化加载策略
        self._state_access_count: Dict[str, int] = {module: 0 for module in self.state_config.keys()}

        # 性能优化配置
        self._cache_enabled = True
        self._cache_timeout = 3600  # 缓存超时时间（秒）
        self._last_cache_update: Dict[str, float] = {}


    def _init_data_dir(self):
        """初始化数据目录"""
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True)

    @measure_performance
    def _init_all_states(self):
        """初始化所有系统状态（延迟加载）"""
        print("🚀 初始化系统状态管理")
        total_states = 0

        for module_name, config in self.state_config.items():
            state_file = self.data_dir / config["file"]

            if not state_file.exists():
                default_state = config["default"]()
                self._save_state(module_name, default_state)
                print(f"✅ 初始化 {module_name} 状态")
                total_states += 1
            else:
                # 状态加载改为在首次使用时进行，避免不必要的IO操作
                print(f"✅ 配置 {module_name} 状态（延迟加载）")
                total_states += 1

        print(f"📊 系统状态管理初始化完成: {total_states} 个状态模块")

    @measure_performance
    def _load_state(self, module_name: str) -> Dict[str, Any]:
        """加载指定模块的状态（优化版本）"""
        config = self.state_config[module_name]
        state_file = self.data_dir / config["file"]

        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            return state_data
        except Exception as e:
            print(f"⚠️  加载 {module_name} 状态失败: {e}")
            default_state = config["default"]()
            self._save_state(module_name, default_state)
            return default_state

    @measure_performance
    def _save_state(self, module_name: str, state_data: Dict[str, Any]):
        """保存指定模块的状态（优化版本）"""
        config = self.state_config[module_name]
        state_file = self.data_dir / config["file"]

        try:
            # 优化JSON序列化，去掉不必要的格式化以提升性能
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  保存 {module_name} 状态失败: {e}")

    @measure_performance
    def get_state(self, module_name: str, key: Optional[str] = None) -> Any:
        """
        获取系统状态（优化版本）

        Args:
            module_name: 模块名称
            key: 可选，状态键名

        Returns:
            状态值（字典或特定值）
        """
        # 更新访问统计
        self._state_access_count[module_name] += 1

        # 检查状态是否需要重新加载（超时检查）
        current_time = datetime.now().timestamp()
        if (module_name not in self._last_cache_update or
            current_time - self._last_cache_update[module_name] > self._cache_timeout):
            if module_name in self._state_cache:
                del self._state_cache[module_name]
                self._loaded_modules.remove(module_name)

        # 延迟加载
        if module_name not in self._state_cache:
            self._state_cache[module_name] = self._load_state(module_name)
            self._loaded_modules.add(module_name)
            self._last_cache_update[module_name] = current_time

        if key:
            return self._state_cache[module_name].get(key)
        else:
            return self._state_cache[module_name]

    @measure_performance
    def get_state_statistics(self) -> Dict[str, Any]:
        """
        获取状态管理统计信息

        Returns:
            状态管理统计数据
        """
        return {
            "total_modules": len(self.state_config),
            "loaded_modules": len(self._loaded_modules),
            "cache_hits": sum(1 for module in self._loaded_modules if module in self._state_cache),
            "access_counts": self._state_access_count,
            "last_cache_update": {module: datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
                                for module, t in self._last_cache_update.items()},
            "memory_usage": self._estimate_memory_usage()
        }

    def _estimate_memory_usage(self) -> float:
        """
        估算状态管理的内存使用

        Returns:
            内存使用量（MB）
        """
        import sys
        total_memory = sys.getsizeof(self._state_cache)
        for module, state in self._state_cache.items():
            total_memory += sys.getsizeof(state)
            for key, value in state.items():
                total_memory += sys.getsizeof(key) + sys.getsizeof(value)

        return total_memory / (1024 * 1024)

    def optimize_cache(self):
        """
        优化状态缓存，根据访问频率和内存使用进行调整
        """
        if len(self._state_cache) > len(self.state_config) * 0.7:
            # 找到访问最少的模块
            least_used_module = min(self._state_access_count.items(), key=lambda x: x[1])[0]
            if least_used_module in self._state_cache:
                del self._state_cache[least_used_module]
                self._loaded_modules.remove(least_used_module)
                self._state_access_count[least_used_module] = 0
                print(f"📉 优化状态缓存：移除访问最少的 {least_used_module} 模块")

    @measure_performance
    def set_state(self, module_name: str, key: str, value: Any) -> bool:
        """
        设置系统状态

        Args:
            module_name: 模块名称
            key: 状态键名
            value: 状态值

        Returns:
            是否设置成功
        """
        try:
            if module_name not in self._state_cache:
                self._state_cache[module_name] = self._load_state(module_name)

            self._state_cache[module_name][key] = value
            self._save_state(module_name, self._state_cache[module_name])
            return True
        except Exception as e:
            print(f"⚠️  设置 {module_name} 状态失败: {e}")
            return False

    @measure_performance
    def update_state(self, module_name: str, updates: Dict[str, Any]) -> bool:
        """
        更新系统状态

        Args:
            module_name: 模块名称
            updates: 更新的状态字典

        Returns:
            是否更新成功
        """
        try:
            if module_name not in self._state_cache:
                self._state_cache[module_name] = self._load_state(module_name)

            self._state_cache[module_name].update(updates)
            self._save_state(module_name, self._state_cache[module_name])
            return True
        except Exception as e:
            print(f"⚠️  更新 {module_name} 状态失败: {e}")
            return False

    @measure_performance
    def get_global_state(self) -> Dict[str, Any]:
        """
        获取全局系统状态
        返回所有模块的状态信息

        Returns:
            全局状态字典
        """
        global_state = {}
        for module_name in self.state_config.keys():
            try:
                module_state = self.get_state(module_name)
                global_state[module_name] = module_state
            except Exception as e:
                print(f"⚠️  获取 {module_name} 状态失败: {e}")
                global_state[module_name] = {}

        return global_state

    @measure_performance
    def save_global_state(self) -> bool:
        """
        保存所有状态到文件
        用于系统退出时的完整状态保存

        Returns:
            是否保存成功
        """
        all_successful = True
        for module_name in self._state_cache.keys():
            try:
                self._save_state(module_name, self._state_cache[module_name])
            except Exception as e:
                print(f"⚠️  保存 {module_name} 状态失败: {e}")
                all_successful = False

        return all_successful

    @measure_performance
    def reset_state(self, module_name: Optional[str] = None):
        """
        重置系统状态

        Args:
            module_name: 可选，模块名称（None表示所有模块）
        """
        if module_name:
            if module_name in self.state_config:
                default_state = self.state_config[module_name]["default"]()
                self._save_state(module_name, default_state)
                self._state_cache[module_name] = default_state
                print(f"✅ 重置 {module_name} 状态")
            else:
                print(f"⚠️  模块 {module_name} 未在状态配置中")
        else:
            # 重置所有模块
            for module_name, config in self.state_config.items():
                default_state = config["default"]()
                self._save_state(module_name, default_state)
                self._state_cache[module_name] = default_state
                print(f"✅ 重置 {module_name} 状态")

    @measure_performance
    def get_state_summary(self) -> Dict[str, Any]:
        """
        获取系统状态摘要

        Returns:
            包含状态计数和基本信息的字典
        """
        summary = {
            "total_modules": len(self.state_config),
            "cached_modules": len(self._state_cache),
            "file_count": len(list(self.data_dir.glob("*.json"))),
            "data_dir_size": self._get_dir_size(self.data_dir),
            "last_update": datetime.now().isoformat(),
            "modules": {}
        }

        for module_name, config in self.state_config.items():
            state_file = self.data_dir / config["file"]
            module_summary = {
                "file_size": self._get_file_size(state_file),
                "exists": state_file.exists()
            }

            if module_name in self._state_cache:
                module_summary["in_cache"] = True
                module_summary["keys_count"] = len(self._state_cache[module_name])
            else:
                module_summary["in_cache"] = False

            summary["modules"][module_name] = module_summary

        return summary

    def _get_file_size(self, file_path: Path) -> int:
        """获取文件大小（字节）"""
        try:
            return file_path.stat().st_size
        except:
            return 0

    def _get_dir_size(self, directory: Path) -> int:
        """获取目录大小（字节）"""
        total = 0
        for entry in directory.glob("*.json"):
            if entry.is_file():
                try:
                    total += entry.stat().st_size
                except:
                    pass
        return total

    # ============================ 状态默认值方法 ============================

    def _get_active_state_defaults(self) -> Dict[str, Any]:
        """获取主动沟通系统默认状态"""
        return {
            "last_interaction": datetime.now().isoformat(),
            "learning_stage": "beginner",
            "projects_completed": 1,
            "communication_count": 0,
            "response_count": 0,
            "last_suggestion": "Python数据分析项目",
            "current_goal": "每天学习至少10个项目"
        }

    def _get_continuous_state_defaults(self) -> Dict[str, Any]:
        """获取持续学习系统默认状态"""
        return {
            "last_learning_time": datetime.now().isoformat(),
            "learning_count": 0,
            "learning_duration": 0.0,
            "interests": [
                "机器学习", "深度学习", "自然语言处理",
                "认知科学", "人工智能伦理", "知识图谱"
            ],
            "resources": [
                "GitHub热门项目", "arXiv论文", "Medium技术文章",
                "知乎问答", "TechCrunch新闻"
            ],
            "learned_topics": [],
            "learning_effectiveness": 0.85,
            "knowledge_growth": 0.0,
            "search_frequency": "high"
        }

    def _get_cognitive_state_defaults(self) -> Dict[str, Any]:
        """获取认知架构系统默认状态"""
        import uuid
        return {
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

    def _get_self_learning_state_defaults(self) -> Dict[str, Any]:
        """获取自我学习系统默认状态"""
        return {"records": []}

    def _get_jarvis_state_defaults(self) -> Dict[str, Any]:
        """获取Jarvis系统默认状态"""
        return {
            "status": "active",
            "last_checked": datetime.now().isoformat(),
            "system_health": "good"
        }

    def _get_learning_progress_defaults(self) -> Dict[str, Any]:
        """获取学习进度系统默认状态"""
        return {
            "total_study_time": 0,
            "projects_studied": [],
            "knowledge_points": [],
            "learning_effectiveness": 0.85,
            "communication_effectiveness": 0.92,
            "improvements": [],
            "vulnerabilities_fixed": 0
        }

    def _get_system_state_defaults(self) -> Dict[str, Any]:
        """获取系统状态默认状态"""
        return {
            "version": "1.0.0",
            "last_optimized": datetime.now().isoformat(),
            "performance_score": 100,
            "errors_count": 0
        }

    def _get_knowledge_base_defaults(self) -> Any:
        """获取知识库系统默认状态"""
        from knowledge_base import KnowledgeBase
        return KnowledgeBase()._get_default_knowledge()

    def _get_vulnerabilities_defaults(self) -> Dict[str, Any]:
        """获取漏洞管理系统默认状态"""
        return {
            "vulnerabilities": [],
            "fixed_count": 0
        }


def test_system_state_manager():
    """测试系统状态管理模块"""
    print("🎯 测试系统状态管理")
    print("=" * 60)

    try:
        manager = SystemStateManager()

        # 获取全局状态摘要
        print("\n📊 系统状态摘要")
        summary = manager.get_state_summary()
        print(f"总模块数: {summary['total_modules']}")
        print(f"缓存模块数: {summary['cached_modules']}")
        print(f"文件数量: {summary['file_count']}")
        print(f"数据目录大小: {summary['data_dir_size']} 字节")

        # 测试获取和设置状态
        print("\n🔍 状态操作测试")
        active_state = manager.get_state("active")
        print(f"主动沟通状态: {len(active_state)} 个字段")

        # 测试设置状态
        test_value = f"测试值_{datetime.now().strftime('%H%M%S')}"
        success = manager.set_state("active", "test_field", test_value)
        print(f"设置状态 {'成功' if success else '失败'}")

        if success:
            retrieved = manager.get_state("active", "test_field")
            print(f"检索状态值: {retrieved}")

        # 测试更新状态
        print("\n🎯 更新状态测试")
        update_success = manager.update_state("system", {
            "performance_score": 95,
            "last_optimized": datetime.now().isoformat()
        })
        print(f"更新状态 {'成功' if update_success else '失败'}")

        if update_success:
            system_state = manager.get_state("system")
            print(f"性能得分: {system_state['performance_score']}")
            print(f"最后优化: {system_state['last_optimized']}")

        print("\n✅ 系统状态管理测试完成")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    test_system_state_manager()
