#!/usr/bin/env python3
"""
🔄 Hermes Agent系统集成
将协议解析器、专家系统和知识管理系统整合到一起
"""

import sys
import os
from typing import Dict, Any
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hermes_protocol import HermesProtocol, HermesInterface
from expert_system import ExpertSystem
from knowledge_base import KnowledgeBase


class HermesSystem:
    """
    Hermes Agent系统集成类
    """

    def __init__(self):
        """
        初始化系统
        """
        self.protocol = HermesProtocol()
        self.interface = HermesInterface(self.protocol)
        self.expert_system = ExpertSystem()
        self.knowledge_base = KnowledgeBase()

        print("🚀 Hermes系统初始化完成")
        self._connect()

    def _connect(self):
        """
        连接到系统
        """
        try:
            self.interface.connect("http://localhost:8080")
            print("✅ 系统连接成功")

        except Exception as e:
            print("⚠️  系统连接失败，使用模拟模式: {}".format(e))
            self.connection_status = "simulated"

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理任务

        Args:
            task: 任务信息

        Returns:
            处理结果
        """
        task_type = task.get("type", "unknown")
        print("📋 开始处理任务: {}".format(task_type))

        if task_type == "project_analysis":
            return self._process_project_analysis(task)
        elif task_type == "knowledge_management":
            return self._process_knowledge_management(task)
        elif task_type == "expert_consultation":
            return self._process_expert_consultation(task)
        elif task_type == "learning_management":
            return self._process_learning_management(task)
        else:
            return self._process_generic_task(task)

    def _process_project_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理项目分析任务

        Args:
            task: 任务信息

        Returns:
            处理结果
        """
        results = []

        # 项目搜索
        keyword = task.get("keyword", "Python")
        search_query = task.get("search_query", keyword)

        try:
            print("🔍 搜索项目: {}".format(search_query))
            projects = self.interface.send_query("project_search", {"keyword": search_query})

            if projects.get("status") == "success":
                for project in projects["data"]:
                    results.append({
                        "name": project["name"],
                        "description": project["description"],
                        "language": project["language"]
                    })

                print("✅ 找到 {} 个项目".format(len(results)))

        except Exception as e:
            print("❌ 项目分析失败: {}".format(e))

        return {
            "status": "success",
            "data": results,
            "message": "项目分析完成"
        }

    def _process_knowledge_management(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理知识管理任务

        Args:
            task: 任务信息

        Returns:
            处理结果
        """
        operation = task.get("operation", "retrieve")

        if operation == "retrieve":
            query = task.get("query", "Python")
            results = self.knowledge_base.retrieve_knowledge(query)

            return {
                "status": "success",
                "data": [
                    {
                        "topic": item["topic"],
                        "content": item["content"]
                    } for item in results
                ],
                "message": "知识检索完成"
            }

        elif operation == "learn":
            knowledge = task.get("knowledge", {})
            if self.knowledge_base.learn_from_experience(knowledge):
                return {
                    "status": "success",
                    "message": "知识学习成功"
                }
            else:
                return {
                    "status": "error",
                    "message": "知识学习失败"
                }

        else:
            return {
                "status": "unknown",
                "message": "未知操作"
            }

    def _process_expert_consultation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理专家咨询任务

        Args:
            task: 任务信息

        Returns:
            处理结果
        """
        task_type = task.get("task_type", "Python")
        skills = task.get("skills", ["Python", "数据分析"])

        expert = self.expert_system.select_expert(task_type, skills)

        if expert:
            return {
                "status": "success",
                "data": {
                    "name": expert["name"],
                    "role": expert["role"],
                    "skills": expert["skills"],
                    "description": expert["description"]
                },
                "message": "专家咨询完成"
            }
        else:
            return {
                "status": "error",
                "message": "未找到匹配的专家"
            }

    def _process_learning_management(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理学习管理任务

        Args:
            task: 任务信息

        Returns:
            处理结果
        """
        project_name = task.get("project", "Python数据分析项目")

        results = []

        # 查找项目相关专家
        experts = self.expert_system.search_experts("Python")

        for expert in experts:
            for project in expert.get("projects", []):
                if project_name in project["name"]:
                    results.append({
                        "name": expert["name"],
                        "project": project["name"],
                        "expertise": expert["role"],
                        "source": project["source"]
                    })

        return {
            "status": "success",
            "data": results,
            "message": "学习管理完成"
        }

    def _process_generic_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理通用任务

        Args:
            task: 任务信息

        Returns:
            处理结果
        """
        task_content = task.get("content", "")

        # 根据内容自动决定处理方式
        if "项目" in task_content or "analysis" in task_content.lower():
            return self._process_project_analysis(task)
        elif "知识" in task_content or "learn" in task_content.lower():
            return self._process_knowledge_management(task)
        elif "专家" in task_content or "consultation" in task_content.lower():
            return self._process_expert_consultation(task)
        elif "学习" in task_content or "management" in task_content.lower():
            return self._process_learning_management(task)
        else:
            return {
                "status": "unknown",
                "message": "未知任务类型"
            }

    def generate_report(self) -> Dict[str, Any]:
        """
        生成系统报告

        Returns:
            报告内容
        """
        statistics = {
            "protocol": "OpenClaw/Hermes 1.0",
            "experts": {
                "count": len(self.expert_system.experts),
                "categories": len(self.expert_system.categories),
                "roles": len(self.expert_system.roles)
            },
            "knowledge": {
                "count": len(self.knowledge_base.knowledge),
                "categories": len(self.knowledge_base.categories),
                "topics": len(self.knowledge_base.topics)
            }
        }

        return {
            "status": "success",
            "data": statistics,
            "message": "系统报告生成完成"
        }

    def shutdown(self):
        """
        关闭系统
        """
        try:
            self.interface.disconnect()
            print("🔌 系统已关闭")

        except Exception as e:
            print("⚠️  系统关闭异常: {}".format(e))


if __name__ == "__main__":
    print("🚀 Hermes系统集成测试")
    print("=" * 60)

    system = HermesSystem()

    print()

    print("🔄 测试项目分析任务:")
    project_task = {
        "type": "project_analysis",
        "keyword": "Python",
        "search_query": "Python数据分析"
    }
    project_results = system.process_task(project_task)
    if project_results["status"] == "success":
        print("✅ 找到 {} 个项目".format(len(project_results["data"])))
        for project in project_results["data"]:
            print("  • {} - {}".format(project["name"], project["language"]))

    print()

    print("🔄 测试知识管理任务:")
    knowledge_task = {
        "type": "knowledge_management",
        "operation": "retrieve",
        "query": "机器学习"
    }
    knowledge_results = system.process_task(knowledge_task)
    if knowledge_results["status"] == "success":
        print("✅ 找到 {} 个知识条目".format(len(knowledge_results["data"])))
        for item in knowledge_results["data"]:
            print("  • {}".format(item["topic"]))

    print()

    print("🔄 测试专家咨询任务:")
    expert_task = {
        "type": "expert_consultation",
        "task_type": "数据分析",
        "skills": ["Python", "Pandas"]
    }
    expert_results = system.process_task(expert_task)
    if expert_results["status"] == "success":
        print("✅ 找到专家: {}".format(expert_results["data"]["name"]))
        print("📝 角色: {}".format(expert_results["data"]["role"]))
        print("🛠️  技能: {}".format(", ".join(expert_results["data"]["skills"])))

    print()

    print("📊 测试系统报告:")
    report = system.generate_report()
    print("专家系统: {}".format(report["data"]["experts"]["count"]))
    print("知识系统: {}".format(report["data"]["knowledge"]["count"]))

    print()

    system.shutdown()

    print()
    print("🎉 Hermes系统集成测试完成!")
