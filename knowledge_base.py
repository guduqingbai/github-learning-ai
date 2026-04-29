#!/usr/bin/env python3
"""
📚 知识管理系统 - Knowledge Base System
实现Hermes Agent风格的知识管理和推理系统
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import time

class KnowledgeBase:
    """
    知识管理系统类
    """

    def __init__(self):
        """
        初始化知识管理系统
        """
        self.knowledge = {}
        self.categories = set()
        self.topics = set()
        self.data_dir = Path("data")
        self.knowledge_file = self.data_dir / "knowledge_base.json"

        self._initialize_data_dir()
        self._load_knowledge()

    def _initialize_data_dir(self):
        """
        初始化数据目录
        """
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True)

        if not self.knowledge_file.exists():
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self._get_default_knowledge(), f, ensure_ascii=False, indent=2)

    def _load_knowledge(self):
        """
        从文件加载知识数据
        """
        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                knowledge_data = json.load(f)

            for item in knowledge_data:
                self.knowledge[item["topic"]] = item
                if "category" in item:
                    self.categories.add(item["category"])
                self.topics.add(item["topic"])

            print("✅ 已加载 {} 个知识条目".format(len(self.knowledge)))
            print("📊 知识类别: {} 个".format(len(self.categories)))
            print("🎯 知识主题: {} 个".format(len(self.topics)))

        except Exception as e:
            print("❌ 加载知识数据失败: {}".format(e))

    def _get_default_knowledge(self) -> List[Dict[str, Any]]:
        """
        获取默认知识数据
        """
        return [
            {
                "topic": "机器学习基础",
                "category": "数据科学",
                "content": "机器学习是计算机系统通过经验自动改进性能的过程。主要包括监督学习、无监督学习和强化学习。",
                "source": "Wikipedia",
                "keywords": ["机器学习", "监督学习", "无监督学习", "强化学习"],
                "references": [
                    {
                        "name": "机器学习入门",
                        "url": "https://github.com/trekhleb/machine-learning-examples"
                    }
                ]
            },
            {
                "topic": "深度学习",
                "category": "数据科学",
                "content": "深度学习是机器学习的一个分支，使用神经网络进行模式识别。主要应用于图像识别、自然语言处理等领域。",
                "source": "TensorFlow文档",
                "keywords": ["深度学习", "神经网络", "图像识别", "自然语言处理"],
                "references": [
                    {
                        "name": "TensorFlow官方文档",
                        "url": "https://www.tensorflow.org/learn"
                    }
                ]
            },
            {
                "topic": "Python数据分析",
                "category": "工程",
                "content": "Python是数据分析领域的主流语言，常用工具包括Pandas、NumPy和Matplotlib。Pandas用于数据处理，NumPy用于数值计算，Matplotlib用于可视化。",
                "source": "数据分析实战",
                "keywords": ["Python", "数据分析", "Pandas", "NumPy", "Matplotlib"],
                "references": [
                    {
                        "name": "Pandas官方文档",
                        "url": "https://pandas.pydata.org/"
                    }
                ]
            },
            {
                "topic": "微服务架构",
                "category": "工程",
                "content": "微服务架构将应用程序拆分为小的、独立的服务，每个服务专注于单一功能。常用技术包括Spring Boot、Docker和Kubernetes。",
                "source": "微服务架构设计",
                "keywords": ["微服务", "Spring Boot", "Docker", "Kubernetes"],
                "references": [
                    {
                        "name": "Spring Boot官方文档",
                        "url": "https://spring.io/projects/spring-boot"
                    }
                ]
            },
            {
                "topic": "Docker容器技术",
                "category": "运维",
                "content": "Docker是一种容器化技术，允许应用程序在隔离的环境中运行。简化了部署和开发流程，提高了一致性。",
                "source": "Docker官方文档",
                "keywords": ["Docker", "容器", "容器化", "部署"],
                "references": [
                    {
                        "name": "Docker官方文档",
                        "url": "https://docs.docker.com/"
                    }
                ]
            }
        ]

    def retrieve_knowledge(self, query: str, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """
        根据查询和关键词检索知识

        Args:
            query: 查询内容
            keywords: 关键词列表

        Returns:
            匹配的知识条目列表
        """
        results = []
        query = query.lower()

        for topic, item in self.knowledge.items():
            score = 0

            # 主题匹配
            if query in topic.lower() or topic.lower() in query:
                score += 10

            # 内容匹配
            if query in item.get("content", "").lower():
                score += 5

            # 关键词匹配
            if keywords:
                for keyword in keywords:
                    if keyword.lower() in item.get("keywords", []):
                        score += 3

            # 分类匹配
            if "category" in item and query in item["category"].lower():
                score += 2

            # 知识重要性匹配（根据时间和流行度）
            if "importance" in item:
                score += item["importance"] * 2

            if score > 0:
                results.append((score, item))

        # 按得分排序
        results.sort(key=lambda x: x[0], reverse=True)

        print("🔍 找到 {} 个匹配知识条目".format(len(results)))

        return [item for score, item in results]

    def learn_from_experience(self, experience: Dict[str, Any]) -> bool:
        """
        从经验中学习

        Args:
            experience: 经验数据

        Returns:
            是否学习成功
        """
        if "topic" not in experience or "content" not in experience:
            return False

        topic = experience["topic"]
        content = experience["content"]

        if topic in self.knowledge:
            # 更新已存在的知识
            self.knowledge[topic]["content"] = content
            if "keywords" in experience:
                self.knowledge[topic]["keywords"] = experience["keywords"]
            if "references" in experience:
                self.knowledge[topic]["references"] = experience["references"]
        else:
            # 添加新知识
            self.knowledge[topic] = experience
            if "category" in experience:
                self.categories.add(experience["category"])
            self.topics.add(topic)

        try:
            self._save_knowledge()
            print("✅ 成功学习新知识: {}".format(topic))
            return True

        except Exception as e:
            print("❌ 学习失败: {}".format(e))
            return False

    def infer_related_topics(self, topic: str) -> List[Dict[str, Any]]:
        """
        推理相关主题

        Args:
            topic: 主题名称

        Returns:
            相关主题列表
        """
        if topic not in self.knowledge:
            return []

        topic_item = self.knowledge[topic]
        related = []

        # 基于关键词相似度推理
        current_keywords = set(topic_item.get("keywords", []))

        for other_topic, other_item in self.knowledge.items():
            if other_topic != topic:
                other_keywords = set(other_item.get("keywords", []))
                intersection = current_keywords & other_keywords

                if len(intersection) > 0:
                    related.append({
                        "topic": other_topic,
                        "similarity": len(intersection),
                        "category": other_item.get("category"),
                        "content": other_item.get("content", "")[:100] + "..."
                    })

        # 基于分类推理
        category = topic_item.get("category", "")
        if category:
            for other_topic, other_item in self.knowledge.items():
                if other_topic != topic and other_item.get("category") == category:
                    found = False
                    for item in related:
                        if item["topic"] == other_topic:
                            found = True
                            break
                    if not found:
                        related.append({
                            "topic": other_topic,
                            "similarity": 1,
                            "category": category,
                            "content": other_item.get("content", "")[:100] + "..."
                        })

        # 按相似度排序
        related.sort(key=lambda x: x["similarity"], reverse=True)

        return related

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取知识管理系统统计信息

        Returns:
            统计信息
        """
        statistics = {
            "total_items": len(self.knowledge),
            "categories": len(self.categories),
            "topics": len(self.topics),
            "keywords": []
        }

        all_keywords = set()
        for item in self.knowledge.values():
            for keyword in item.get("keywords", []):
                all_keywords.add(keyword)

        statistics["keywords"] = list(all_keywords)

        return statistics

    def get_category_breakdown(self) -> Dict[str, int]:
        """
        获取知识类别分布

        Returns:
            类别分布字典
        """
        category_count = {}

        for item in self.knowledge.values():
            category = item.get("category", "其他")
            category_count[category] = category_count.get(category, 0) + 1

        return dict(sorted(category_count.items(), key=lambda x: x[1], reverse=True))

    def add_knowledge(self, knowledge: Dict[str, Any]) -> bool:
        """
        添加新知识

        Args:
            knowledge: 知识信息

        Returns:
            是否添加成功
        """
        if "topic" not in knowledge:
            return False

        self.knowledge[knowledge["topic"]] = knowledge

        if "category" in knowledge:
            self.categories.add(knowledge["category"])
        self.topics.add(knowledge["topic"])

        try:
            self._save_knowledge()
            print("✅ 成功添加知识: {}".format(knowledge["topic"]))
            return True

        except Exception as e:
            print("❌ 保存知识数据失败: {}".format(e))
            return False

    def remove_knowledge(self, topic: str) -> bool:
        """
        删除知识

        Args:
            topic: 主题名称

        Returns:
            是否删除成功
        """
        if topic in self.knowledge:
            del self.knowledge[topic]

            try:
                self._save_knowledge()
                print("✅ 成功删除知识: {}".format(topic))
                return True

            except Exception as e:
                print("❌ 删除知识失败: {}".format(e))
                return False

        return False

    def update_knowledge(self, topic: str, updates: Dict[str, Any]) -> bool:
        """
        更新知识信息

        Args:
            topic: 主题名称
            updates: 更新信息

        Returns:
            是否更新成功
        """
        if topic not in self.knowledge:
            return False

        self.knowledge[topic].update(updates)

        if "category" in updates:
            self.categories.add(updates["category"])

        try:
            self._save_knowledge()
            print("✅ 成功更新知识: {}".format(topic))
            return True

        except Exception as e:
            print("❌ 更新知识信息失败: {}".format(e))
            return False

    def _save_knowledge(self):
        """
        保存知识数据到文件
        """
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.knowledge.values()), f, ensure_ascii=False, indent=2)

        except Exception as e:
            print("❌ 保存知识数据失败: {}".format(e))


if __name__ == "__main__":
    print("🚀 知识管理系统测试")
    print("=" * 60)

    system = KnowledgeBase()

    print()

    print("📚 测试知识检索:")
    retrieved = system.retrieve_knowledge("机器学习")
    if retrieved:
        print("检索结果:")
        for item in retrieved:
            print("  • {}".format(item["topic"]))
            print("    {}".format(item["content"]))

    print()

    print("🔗 测试推理功能:")
    related = system.infer_related_topics("机器学习基础")
    if related:
        print("相关主题:")
        for item in related:
            print("  • {} (相似度: {})".format(item["topic"], item["similarity"]))

    print()

    print("➕ 测试学习功能:")
    new_knowledge = {
        "topic": "深度学习框架",
        "category": "数据科学",
        "content": "深度学习框架提供了构建和训练神经网络的工具，常用的框架包括TensorFlow和PyTorch。",
        "source": "PyTorch官方文档",
        "keywords": ["深度学习", "框架", "TensorFlow", "PyTorch"],
        "references": [
            {
                "name": "PyTorch官方文档",
                "url": "https://pytorch.org/docs"
            }
        ]
    }

    learned = system.learn_from_experience(new_knowledge)
    if learned:
        print("✅ 成功学习新知识")

    print()

    print("📊 测试统计功能:")
    stats = system.get_statistics()
    print("知识条目: {}".format(stats["total_items"]))
    print("知识类别: {}".format(stats["categories"]))
    print("关键词数量: {}".format(len(stats["keywords"])))

    print()

    print("📈 测试类别分布:")
    category_dist = system.get_category_breakdown()
    for category, count in category_dist.items():
        print("{}: {} 条".format(category, count))

    print()

    print("🎉 知识管理系统测试完成!")
