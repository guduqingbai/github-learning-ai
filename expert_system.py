#!/usr/bin/env python3
"""
👨‍💼 专家系统 - Expert System
实现Hermes Agent风格的专家角色系统
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

class ExpertSystem:
    """
    专家系统类
    """

    def __init__(self):
        """
        初始化专家系统
        """
        self.experts = {}
        self.categories = set()
        self.roles = set()
        self.data_dir = Path("data")
        self.experts_file = self.data_dir / "experts.json"

        self._initialize_data_dir()
        self._load_experts()

    def _initialize_data_dir(self):
        """
        初始化数据目录
        """
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True)

        if not self.experts_file.exists():
            with open(self.experts_file, 'w', encoding='utf-8') as f:
                json.dump(self._get_default_experts(), f, ensure_ascii=False, indent=2)

    def _load_experts(self):
        """
        从文件加载专家数据
        """
        try:
            with open(self.experts_file, 'r', encoding='utf-8') as f:
                experts_data = json.load(f)

            for expert in experts_data:
                self.experts[expert["name"]] = expert
                if "category" in expert:
                    self.categories.add(expert["category"])
                if "role" in expert:
                    self.roles.add(expert["role"])

            print("✅ 已加载 {} 个专家".format(len(self.experts)))
            print("📊 专家类别: {} 个".format(len(self.categories)))
            print("🎯 专家角色: {} 个".format(len(self.roles)))

        except Exception as e:
            print("❌ 加载专家数据失败: {}".format(e))

    def _get_default_experts(self) -> List[Dict[str, Any]]:
        """
        获取默认专家数据（基于agency-agents-zh项目）
        """
        return [
            {
                "name": "Python数据分析专家",
                "role": "数据分析",
                "category": "工程",
                "description": "在数据分析领域有5年经验，精通Pandas、NumPy和Matplotlib",
                "skills": ["Python", "Pandas", "NumPy", "Matplotlib", "数据分析"],
                "projects": [
                    {
                        "name": "Python数据分析项目",
                        "description": "使用Pandas和Matplotlib进行数据分析",
                        "source": "GitHub"
                    }
                ]
            },
            {
                "name": "Java后端开发专家",
                "role": "后端开发",
                "category": "工程",
                "description": "在企业级应用开发有8年经验，精通Spring Boot和微服务架构",
                "skills": ["Java", "Spring Boot", "微服务", "Docker", "Kubernetes"],
                "projects": [
                    {
                        "name": "Java网络应用",
                        "description": "基于Spring Boot的Web应用程序",
                        "source": "GitHub"
                    }
                ]
            },
            {
                "name": "前端开发专家",
                "role": "前端开发",
                "category": "工程",
                "description": "在Web开发领域有6年经验，精通Vue.js和React",
                "skills": ["JavaScript", "HTML", "CSS", "Vue.js", "React", "Node.js"],
                "projects": [
                    {
                        "name": "前端组件库",
                        "description": "基于Vue.js的企业级组件库",
                        "source": "GitHub"
                    }
                ]
            },
            {
                "name": "机器学习专家",
                "role": "机器学习",
                "category": "数据科学",
                "description": "在机器学习领域有4年经验，精通Scikit-learn和TensorFlow",
                "skills": ["Python", "Scikit-learn", "TensorFlow", "机器学习", "深度学习"],
                "projects": [
                    {
                        "name": "机器学习项目",
                        "description": "使用Scikit-learn进行数据分析和预测",
                        "source": "GitHub"
                    }
                ]
            },
            {
                "name": "DevOps专家",
                "role": "运维开发",
                "category": "运维",
                "description": "在DevOps领域有5年经验，精通CI/CD和云平台",
                "skills": ["Docker", "Kubernetes", "Jenkins", "GitLab CI", "AWS"],
                "projects": [
                    {
                        "name": "CI/CD自动化",
                        "description": "实现自动化构建和部署流程",
                        "source": "GitHub"
                    }
                ]
            },
            {
                "name": "产品经理",
                "role": "产品管理",
                "category": "管理",
                "description": "在产品管理领域有7年经验，精通用户研究和产品规划",
                "skills": ["产品规划", "用户研究", "数据分析", "沟通协调"],
                "projects": [
                    {
                        "name": "产品规划",
                        "description": "制定产品路线图和功能规划",
                        "source": "内部文档"
                    }
                ]
            },
            {
                "name": "UI/UX设计师",
                "role": "设计",
                "category": "设计",
                "description": "在UI/UX设计领域有5年经验，精通Figma和设计思维",
                "skills": ["Figma", "UI设计", "UX设计", "用户研究", "设计思维"],
                "projects": [
                    {
                        "name": "界面设计",
                        "description": "创建美观易用的用户界面",
                        "source": "内部文档"
                    }
                ]
            }
        ]

    def select_expert(self, task_type: str, skills_required: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        根据任务类型和所需技能选择专家

        Args:
            task_type: 任务类型
            skills_required: 所需技能列表

        Returns:
            最佳匹配的专家，或None
        """
        if not self.experts:
            return None

        candidates = []

        for expert in self.experts.values():
            score = 0

            if task_type.lower() in expert.get("role", "").lower() or \
               task_type.lower() in expert.get("category", "").lower():
                score += 5

            if skills_required:
                expert_skills = expert.get("skills", [])
                matching_skills = len(set(expert_skills) & set(skills_required))
                if matching_skills > 0:
                    score += matching_skills * 2

            expert_projects = sum(len(project.get("source", "")) for project in expert.get("projects", []))
            if expert_projects > 0:
                score += 2

            if score > 0:
                candidates.append((score, expert))

        if not candidates:
            return None

        selected = sorted(candidates, key=lambda x: x[0], reverse=True)[0][1]

        print("🎯 选择专家: {} (得分: {})".format(selected["name"], sorted(candidates, key=lambda x: x[0], reverse=True)[0][0]))

        return selected

    def search_experts(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索专家

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的专家列表
        """
        results = []

        keyword = keyword.lower()

        for expert in self.experts.values():
            if keyword in expert.get("name", "").lower() or \
               keyword in expert.get("role", "").lower() or \
               keyword in expert.get("category", "").lower() or \
               keyword in expert.get("description", "").lower() or \
               any(keyword in skill.lower() for skill in expert.get("skills", [])):
                results.append(expert)

        print("🔍 找到 {} 个匹配专家".format(len(results)))

        return results

    def get_experts_by_role(self, role: str) -> List[Dict[str, Any]]:
        """
        按角色获取专家

        Args:
            role: 角色名称

        Returns:
            该角色的专家列表
        """
        role = role.lower()

        return [
            expert for expert in self.experts.values()
            if role in expert.get("role", "").lower()
        ]

    def get_experts_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        按类别获取专家

        Args:
            category: 类别名称

        Returns:
            该类别下的专家列表
        """
        category = category.lower()

        return [
            expert for expert in self.experts.values()
            if category in expert.get("category", "").lower()
        ]

    def add_expert(self, expert: Dict[str, Any]) -> bool:
        """
        添加新专家

        Args:
            expert: 专家信息

        Returns:
            是否添加成功
        """
        if "name" not in expert:
            return False

        self.experts[expert["name"]] = expert

        if "category" in expert:
            self.categories.add(expert["category"])
        if "role" in expert:
            self.roles.add(expert["role"])

        try:
            self._save_experts()
            print("✅ 成功添加专家: {}".format(expert["name"]))
            return True

        except Exception as e:
            print("❌ 保存专家数据失败: {}".format(e))
            return False

    def remove_expert(self, expert_name: str) -> bool:
        """
        删除专家

        Args:
            expert_name: 专家名称

        Returns:
            是否删除成功
        """
        if expert_name in self.experts:
            del self.experts[expert_name]

            try:
                self._save_experts()
                print("✅ 成功删除专家: {}".format(expert_name))
                return True

            except Exception as e:
                print("❌ 删除专家失败: {}".format(e))
                return False

        return False

    def update_expert(self, expert_name: str, updates: Dict[str, Any]) -> bool:
        """
        更新专家信息

        Args:
            expert_name: 专家名称
            updates: 更新信息

        Returns:
            是否更新成功
        """
        if expert_name not in self.experts:
            return False

        self.experts[expert_name].update(updates)

        if "category" in updates:
            self.categories.add(updates["category"])
        if "role" in updates:
            self.roles.add(updates["role"])

        try:
            self._save_experts()
            print("✅ 成功更新专家: {}".format(expert_name))
            return True

        except Exception as e:
            print("❌ 更新专家信息失败: {}".format(e))
            return False

    def _save_experts(self):
        """
        保存专家数据到文件
        """
        try:
            with open(self.experts_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.experts.values()), f, ensure_ascii=False, indent=2)

        except Exception as e:
            print("❌ 保存专家数据失败: {}".format(e))

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取专家系统统计信息

        Returns:
            统计信息
        """
        statistics = {
            "total_experts": len(self.experts),
            "categories": len(self.categories),
            "roles": len(self.roles),
            "skills": [],
            "projects": []
        }

        all_skills = set()
        all_projects = set()

        for expert in self.experts.values():
            for skill in expert.get("skills", []):
                all_skills.add(skill)
            for project in expert.get("projects", []):
                all_projects.add(project["name"])

        statistics["skills"] = list(all_skills)
        statistics["projects"] = list(all_projects)

        return statistics

    def get_category_breakdown(self) -> Dict[str, int]:
        """
        获取专家类别分布

        Returns:
            类别分布字典
        """
        category_count = {}

        for expert in self.experts.values():
            category = expert.get("category", "其他")
            category_count[category] = category_count.get(category, 0) + 1

        return dict(sorted(category_count.items(), key=lambda x: x[1], reverse=True))

    def get_role_breakdown(self) -> Dict[str, int]:
        """
        获取专家角色分布

        Returns:
            角色分布字典
        """
        role_count = {}

        for expert in self.experts.values():
            role = expert.get("role", "其他")
            role_count[role] = role_count.get(role, 0) + 1

        return dict(sorted(role_count.items(), key=lambda x: x[1], reverse=True))


if __name__ == "__main__":
    print("🚀 专家系统测试")
    print("=" * 60)

    system = ExpertSystem()

    print()

    print("📋 测试专家选择:")
    selected = system.select_expert("数据分析", ["Python", "Pandas"])
    if selected:
        print("✅ 选择专家: {}".format(selected["name"]))
        print("📝 技能: {}".format(', '.join(selected["skills"])))

    print()

    print("🔍 测试搜索功能:")
    search_results = system.search_experts("Python")
    if search_results:
        print("搜索结果:")
        for expert in search_results:
            print("  • {} - {}".format(expert["name"], expert["role"]))

    print()

    print("👨‍💼 测试角色专家:")
    engineering_experts = system.get_experts_by_category("工程")
    if engineering_experts:
        print("工程类别专家: {} 人".format(len(engineering_experts)))
        for expert in engineering_experts:
            print("  • {} - {}".format(expert["name"], expert["role"]))

    print()

    print("➕ 测试添加专家:")
    new_expert = {
        "name": "Go语言开发专家",
        "role": "后端开发",
        "category": "工程",
        "description": "在Go语言开发领域有3年经验，精通高性能服务开发",
        "skills": ["Go", "高性能编程", "微服务", "API开发"],
        "projects": [
            {
                "name": "Go微服务框架",
                "description": "高性能的Go语言微服务框架",
                "source": "GitHub"
            }
        ]
    }

    added = system.add_expert(new_expert)
    if added:
        print("✅ 成功添加: {}".format(new_expert["name"]))

    print()

    print("📊 测试统计功能:")
    stats = system.get_statistics()
    print("专家总数: {}".format(stats["total_experts"]))
    print("技能数量: {}".format(len(stats["skills"])))
    print("项目数量: {}".format(len(stats["projects"])))

    print()

    print("📈 测试类别分布:")
    category_dist = system.get_category_breakdown()
    for category, count in category_dist.items():
        print("{}: {} 人".format(category, count))

    print()

    print("🎉 专家系统测试完成!")
