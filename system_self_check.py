#!/usr/bin/env python3
"""
🎯 系统自检与健康检查模块
提供系统完整性、功能可用性、配置正确性检查
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import json

from system_state_manager import SystemStateManager
from system_interfaces import get_system_interface
from continuous_learning import ContinuousLearningSystem
from cognitive_architecture import test_cognitive_architecture
from run_demonstration import run_demonstration


class SystemSelfCheck:
    """系统自检与健康检查类"""

    def __init__(self):
        """初始化自检系统"""
        self.state_manager = SystemStateManager()
        self.interface = get_system_interface()
        self.checks = [
            self.check_system_configuration,
            self.check_state_manager,
            self.check_interface_availability,
            self.check_continuous_learning,
            self.check_cognitive_architecture,
            self.check_browser_integration,
            self.check_data_availability,
            self.check_performance_optimization,
            self.check_local_learning_features
        ]
        self.results = []

    def run_full_check(self) -> bool:
        """运行完整的系统自检"""
        print("🎯 系统自检与健康检查")
        print("=" * 60)

        all_passed = True
        for i, check in enumerate(self.checks, 1):
            try:
                print(f"\n🔍 检查 {i}/{len(self.checks)}: {check.__doc__}")
                result = check()
                self.results.append({
                    "check": check.__doc__,
                    "passed": result,
                    "time": datetime.now().isoformat()
                })
                if result:
                    print("✅ 通过")
                else:
                    print("❌ 失败")
                    all_passed = False
            except Exception as e:
                print(f"❌ 错误: {e}")
                self.results.append({
                    "check": check.__doc__,
                    "passed": False,
                    "time": datetime.now().isoformat(),
                    "error": str(e)
                })
                all_passed = False

        self._print_check_summary()
        return all_passed

    def check_system_configuration(self) -> bool:
        """系统配置检查"""
        try:
            # 检查必要的Python版本
            if sys.version_info < (3, 8):
                return False

            # 检查项目结构
            required_files = [
                "system_state_manager.py",
                "system_interfaces.py",
                "continuous_learning.py",
                "cognitive_architecture.py",
                "browser_integration.py",
                "run_demonstration.py"
            ]

            for file_name in required_files:
                if not Path(file_name).exists():
                    print(f"❌ 缺少文件: {file_name}")
                    return False

            return True
        except Exception as e:
            print(f"❌ 配置检查失败: {e}")
            return False

    def check_state_manager(self) -> bool:
        """状态管理系统检查"""
        try:
            state = self.state_manager.get_global_state()
            if not state or len(state) < 5:
                return False

            # 检查必要的状态模块
            required_modules = ["active", "continuous", "cognitive", "learning", "system"]
            for module in required_modules:
                if module not in state:
                    print(f"❌ 状态模块缺失: {module}")
                    return False

            return True
        except Exception as e:
            print(f"❌ 状态管理检查失败: {e}")
            return False

    def check_interface_availability(self) -> bool:
        """系统接口可用性检查"""
        try:
            # 检查学习接口
            learning_info = self.interface.learning.get_learning_state()
            if not learning_info:
                return False

            # 检查沟通接口
            communication_info = self.interface.communication.get_communication_state()
            if not communication_info:
                return False

            # 检查认知接口
            cognitive_info = self.interface.cognitive.get_cognitive_state()
            if not cognitive_info:
                return False

            return True
        except Exception as e:
            print(f"❌ 接口检查失败: {e}")
            return False

    def check_continuous_learning(self) -> bool:
        """持续学习系统检查"""
        try:
            learning_system = ContinuousLearningSystem()
            if not learning_system:
                return False

            # 启动学习系统测试
            learning_system.start_continuous_learning()
            time.sleep(2)
            learning_system.stop_learning()

            return True
        except Exception as e:
            print(f"❌ 持续学习检查失败: {e}")
            return False

    def check_cognitive_architecture(self) -> bool:
        """认知架构系统检查"""
        try:
            return test_cognitive_architecture()
        except Exception as e:
            print(f"❌ 认知架构检查失败: {e}")
            return False

    def check_browser_integration(self) -> bool:
        """浏览器集成检查"""
        try:
            from browser_integration import BrowserIntegration
            browser = BrowserIntegration()

            print("🔍 检查浏览器集成配置")
            integration_status = browser.get_browser_integration_status()

            if not integration_status:
                print("❌ 无法获取浏览器集成状态")
                return False

            if integration_status.get("enabled"):
                print("✅ 浏览器集成已启用")
            else:
                print("⚠️  浏览器集成未启用")

            available_browsers = browser.get_available_browsers()
            if available_browsers:
                print(f"✅ 检测到可用浏览器: {', '.join(available_browsers)}")

                # 检查每个可用浏览器的连接状态
                for browser_name in available_browsers:
                    try:
                        config = browser.get_browser_config(browser_name)
                        if config and config.get("enabled"):
                            is_connected, message = browser.test_browser_connection(browser_name)
                            if is_connected:
                                print(f"✅ {browser_name} 连接成功")
                            else:
                                print(f"⚠️  {browser_name} 连接失败: {message}")
                    except Exception as e:
                        print(f"⚠️  检查 {browser_name} 失败: {e}")
            else:
                print("⚠️  未检测到可用的浏览器")

            # 检查本地学习内容分析功能
            print("🔍 检查本地学习内容分析功能")
            local_content_files = ["learning_notes.txt", "study_materials.md", "course_notes.txt"]
            found_local_content = False

            for filename in local_content_files:
                if Path(filename).exists():
                    print(f"✅ 检测到本地学习内容: {filename}")
                    found_local_content = True

            if not found_local_content:
                print("⚠️  未检测到本地学习内容文件")

            return True  # 即使没有浏览器，系统仍可工作
        except Exception as e:
            print(f"❌ 浏览器集成检查失败: {e}")
            import traceback
            print(f"错误详情: {traceback.format_exc()}")
            return False

    def check_performance_optimization(self) -> bool:
        """系统性能优化检查"""
        try:
            # 检查系统状态管理的单例模式实现
            from system_state_manager import SystemStateManager
            manager1 = SystemStateManager()
            manager2 = SystemStateManager()

            if manager1 is not manager2:
                print("❌ 系统状态管理单例模式未正确实现")
                return False

            print("✅ 系统状态管理单例模式实现成功")

            return True
        except Exception as e:
            print(f"❌ 系统性能优化检查失败: {e}")
            import traceback
            print(f"错误详情: {traceback.format_exc()}")
            return False

    def check_local_learning_features(self) -> bool:
        """本地学习功能检查"""
        try:
            # 检查本地学习内容分析功能
            from browser_integration import BrowserIntegration
            browser = BrowserIntegration()

            print("🔍 检查本地学习内容分析功能")
            # 测试本地内容分析方法是否存在
            if hasattr(browser, "_analyze_local_learning_content"):
                print("✅ 本地学习内容分析功能已实现")
            else:
                print("❌ 本地学习内容分析功能未实现")
                return False

            return True
        except Exception as e:
            print(f"❌ 本地学习功能检查失败: {e}")
            import traceback
            print(f"错误详情: {traceback.format_exc()}")
            return False

    def check_data_availability(self) -> bool:
        """数据可用性检查"""
        try:
            data_dir = Path("data")
            if not data_dir.exists():
                data_dir.mkdir()

            # 检查必要的数据文件
            required_files = [
                "active_state.json",
                "continuous_learning_state.json",
                "cognitive_state.json",
                "learning_progress.json",
                "system_state.json"
            ]

            for file_name in required_files:
                file_path = data_dir / file_name
                if not file_path.exists():
                    print(f"⚠️  数据文件不存在: {file_name}")
                    # 尝试初始化状态
                    self.state_manager._init_all_states()

            return True
        except Exception as e:
            print(f"❌ 数据检查失败: {e}")
            return False

    def _print_check_summary(self):
        """打印自检结果摘要"""
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)

        print("\n📊 自检结果摘要")
        print("=" * 60)
        print(f"总检查数: {total}")
        print(f"通过数: {passed}")
        print(f"失败数: {total - passed}")

        if total - passed > 0:
            print("\n❌ 失败的检查:")
            for result in self.results:
                if not result["passed"]:
                    print(f"  - {result['check']}")
                    if "error" in result:
                        print(f"    错误: {result['error']}")

    def save_results(self, filename: str = "self_check_results.json"):
        """保存自检结果到文件"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"\n📄 结果已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")



def run_self_check():
    """运行系统自检"""
    check = SystemSelfCheck()
    try:
        passed = check.run_full_check()
        check.save_results()
        if passed:
            print("\n🎉 系统自检通过！")
            return 0
        else:
            print("\n🚨 系统自检失败！")
            return 1
    except Exception as e:
        print(f"❌ 自检过程中出错: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_self_check())