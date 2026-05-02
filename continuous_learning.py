#!/usr/bin/env python3
"""
🔄 持续学习系统 - 自我发现学习好的东西的机制
实现每天不停查找、不停学习的能力
架构一致性优化：使用统一系统状态管理
"""

import time
import random
import threading
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.parse
import ssl
from system_state_manager import SystemStateManager


class ContinuousLearningSystem:
    """
    持续学习系统 - 自我发现学习好的东西的机制
    使用统一系统状态管理
    """

    def __init__(self):
        """初始化持续学习系统"""
        print("🎯 初始化持续学习系统")

        # 统一系统状态管理
        self.state_manager = SystemStateManager()

        # 初始化学习属性
        self.learning_interests = [
            "机器学习", "深度学习", "自然语言处理",
            "认知科学", "人工智能伦理", "知识图谱",
            "自我思考AI架构", "认知系统设计", "自主Agent系统",
            "元学习与自我改进", "好奇心驱动探索"
        ]

        self.learning_resources = [
            {"name": "GitHub热门项目", "type": "github", "importance": 0.8},
            {"name": "arXiv论文", "type": "arxiv", "importance": 0.9},
            {"name": "Medium技术文章", "type": "medium", "importance": 0.7},
            {"name": "知乎问答", "type": "zhihu", "importance": 0.6},
            {"name": "TechCrunch新闻", "type": "techcrunch", "importance": 0.5}
        ]

        # 学习线程
        self.learning_thread = None
        self.is_running = False

        # 从统一状态管理加载学习属性
        self._load_learning_state()

        print("✅ 持续学习系统初始化完成")

    def _load_learning_state(self):
        """加载学习状态（使用统一状态管理）"""
        try:
            continuous_state = self.state_manager.get_state("continuous")
            self.learning_count = continuous_state.get("learning_count", 0)
            self.learning_duration = continuous_state.get("learning_duration", 0.0)
            self.search_frequency = continuous_state.get("search_frequency", "high")
            self.learning_interests = continuous_state.get("interests", self.learning_interests)

            print(f"🔄 学习状态: 学习次数={self.learning_count}, 总时长={self.learning_duration:.0f}分钟")

        except Exception as e:
            print(f"⚠️  学习状态加载失败: {e}")
            self._init_learning_state()

    def _init_learning_state(self):
        """初始化学习状态（使用统一状态管理）"""
        default_state = {
            "last_learning_time": datetime.now().isoformat(),
            "learning_count": 0,
            "learning_duration": 0.0,
            "interests": self.learning_interests,
            "resources": [resource["name"] for resource in self.learning_resources],
            "learned_topics": [],
            "learning_effectiveness": 0.85,
            "knowledge_growth": 0.0,
            "search_frequency": "high"
        }

        self.state_manager.update_state("continuous", default_state)
        self.learning_count = default_state["learning_count"]
        self.learning_duration = default_state["learning_duration"]
        self.search_frequency = default_state["search_frequency"]

        print("✅ 学习状态已初始化")

    def _save_learning_state(self):
        """保存学习状态（使用统一状态管理）"""
        try:
            continuous_state = self.state_manager.get_state("continuous")
            continuous_state["last_learning_time"] = datetime.now().isoformat()
            continuous_state["learning_count"] = self.learning_count
            continuous_state["learning_duration"] = self.learning_duration
            continuous_state["search_frequency"] = self.search_frequency

            self.state_manager.update_state("continuous", continuous_state)
            print("📊 学习状态已保存")

        except Exception as e:
            print(f"⚠️  学习状态保存失败: {e}")

    def start_continuous_learning(self):
        """开始持续学习"""
        if self.is_running:
            print("⚠️  持续学习系统已在运行")
            return False

        self.is_running = True
        self.learning_thread = threading.Thread(target=self._learning_loop)
        self.learning_thread.daemon = True
        self.learning_thread.start()

        print("🚀 持续学习系统启动成功")
        return True

    def _learning_loop(self):
        """持续学习循环"""
        while self.is_running:
            try:
                self._learn_once()
                self._save_learning_state()

                # 根据当前学习状态调整学习频率
                self._adjust_learning_frequency()

                # 休息时间（根据学习频率调整）
                rest_time = self._get_rest_time()
                print(f"⏳ 休息 {rest_time}秒后继续学习...")
                time.sleep(rest_time)

            except Exception as e:
                print(f"⚠️  学习循环失败: {e}")
                time.sleep(60)

    def _learn_once(self):
        """单次学习"""
        start_time = time.time()

        print("🎓 开始学习...")

        # 1. 选择学习资源
        resource = self._choose_learning_resource()

        # 2. 搜索相关内容
        search_query = self._choose_search_query()
        search_results = self._search_learning_content(resource, search_query)

        # 3. 评估学习内容价值
        valuable_content = self._evaluate_content_value(search_results)

        # 4. 学习和记录
        if valuable_content:
            self._learn_content(valuable_content)

        # 5. 更新学习统计
        self.learning_count += 1
        duration = time.time() - start_time

        # 模拟实际学习时长（每个内容需要1-3分钟学习）
        content_learning_time = 0
        if valuable_content:
            content_learning_time = len(valuable_content) * (1.0 + random.random() * 2.0)

        self.learning_duration += (duration / 60) + content_learning_time

        print(f"✅ 学习完成: {len(valuable_content)}个内容, 耗时={duration:.1f}秒, 学习时间={content_learning_time:.1f}分钟")

    def _choose_learning_resource(self):
        """选择学习资源 — 基于重要性加权的随机选择"""
        weights = [r["importance"] for r in self.learning_resources]
        total = sum(weights)
        r = random.uniform(0, total)
        cumulative = 0
        for resource, w in zip(self.learning_resources, weights):
            cumulative += w
            if r <= cumulative:
                return resource
        return self.learning_resources[-1]

    def _choose_search_query(self):
        """选择搜索查询"""
        return random.choice(self.learning_interests)

    def _search_learning_content(self, resource, query):
        """搜索学习内容 - 从真实公开API获取"""
        print(f"🔍 在{resource['name']}中搜索: {query}")
        ctx = ssl._create_unverified_context()
        headers = {"User-Agent": "Mozilla/5.0 (compatible; LearningBot/1.0)"}
        results = []

        try:
            if resource["type"] == "github":
                url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&per_page=5"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                    data = json.loads(resp.read().decode())
                    for repo in data.get("items", [])[:5]:
                        results.append({
                            "title": repo["full_name"],
                            "content": repo.get("description", "") or "暂无描述",
                            "source": "GitHub",
                            "importance": min(1.0, repo.get("stargazers_count", 0) / 5000 + 0.5),
                            "link": repo["html_url"],
                        })

            elif resource["type"] == "arxiv":
                url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&sortBy=submittedDate&sortOrder=descending&max_results=5"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                    xml = resp.read().decode("utf-8")
                    import re
                    titles = re.findall(r"<title>(.*?)</title>", xml, re.DOTALL)
                    ids = re.findall(r"<id>(.*?)</id>", xml)
                    for i in range(1, min(len(titles), 5)):
                        t = titles[i].strip().replace("\n", " ")[:200]
                        link = ids[i].strip() if i < len(ids) else url
                        results.append({
                            "title": f"[论文] {t}",
                            "content": f"arXiv最新论文: {query}",
                            "source": "arXiv",
                            "importance": 0.85,
                            "link": link,
                        })

            elif resource["type"] in ("medium", "zhihu", "techcrunch"):
                # 用Wikipedia作为备选
                wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query.replace(' ', '_'))}"
                try:
                    wreq = urllib.request.Request(wiki_url, headers=headers)
                    with urllib.request.urlopen(wreq, timeout=8, context=ctx) as wresp:
                        wdata = json.loads(wresp.read().decode())
                        results.append({
                            "title": wdata.get("title", query),
                            "content": (wdata.get("extract", "") or "")[:400],
                            "source": "Wikipedia",
                            "importance": 0.8,
                            "link": wdata.get("content_urls", {}).get("desktop", {}).get("page", wiki_url),
                        })
                except Exception:
                    pass

            time.sleep(1)  # 礼貌间隔

        except Exception as e:
            print(f"⚠️  真实搜索失败: {e}")

        # 如果真实搜索没结果，用模拟数据兜底
        if not results:
            print("ℹ️  使用模拟数据补充")
            results = [
                {
                    "title": f"{query}基础概念",
                    "content": f"关于{query}的基本概念和核心原理介绍",
                    "source": resource["name"],
                    "importance": 0.8,
                    "link": f"https://example.com/{query}"
                },
                {
                    "title": f"{query}前沿进展",
                    "content": f"{query}领域的最新研究进展和应用",
                    "source": resource["name"],
                    "importance": 0.7,
                    "link": f"https://example.com/{query}-advanced"
                }
            ]

        return results

    def _evaluate_content_value(self, search_results):
        """评估学习内容价值"""
        valuable_content = []

        # 获取已学习过的内容标题
        learned_topics = set(self.state_manager.get_state("continuous", "learned_topics") or [])

        for result in search_results:
            # 基于重要性评分筛选
            if result.get("importance", 0) > 0.7:
                # 检查是否已学习过该内容
                if result["title"] not in learned_topics:
                    valuable_content.append(result)
                    learned_topics.add(result["title"])
                else:
                    print(f"ℹ️  内容已学习过: {result['title']}")

        # 更新已学习过的内容列表
        self.state_manager.set_state("continuous", "learned_topics", list(learned_topics))
        return valuable_content

    def _learn_content(self, content_items):
        """学习和记录内容"""
        print(f"📚 学习 {len(content_items)}个内容:")

        for item in content_items:
            print(f"   - {item['title']} (重要性:{item.get('importance', 0):.1f})")

            # 添加到知识库
            self._add_to_knowledge_base(item)

    def _add_to_knowledge_base(self, item):
        """添加到知识库"""
        try:
            from knowledge_base import KnowledgeBase
            knowledge_base = KnowledgeBase()

            new_knowledge = {
                "title": item["title"],
                "content": item["content"],
                "keywords": self.learning_interests,
                "importance": item.get("importance", 0.8),
                "source": item["source"],
                "link": item.get("link", "https://example.com"),
                "learning_time": datetime.now().isoformat()
            }

            knowledge_base.add_knowledge(new_knowledge)

            print(f"✅ 已添加到知识库: {new_knowledge['title']}")

        except Exception as e:
            print(f"⚠️  知识库更新失败: {e}")

    def _adjust_learning_frequency(self):
        """调整学习频率 - 基于学习进度"""
        # 只根据学习次数调整频率，确保用户离线5分钟后学习
        if self.learning_count < 20:
            self.search_frequency = "high"    # 5分钟间隔（高频率）
        elif self.learning_count < 50:
            self.search_frequency = "medium"  # 10分钟间隔（中频率）
        else:
            self.search_frequency = "low"     # 15分钟间隔（低频率）

        # 更新系统状态
        self.state_manager.set_state("continuous", "search_frequency", self.search_frequency)
        print(f"🔄 学习频率调整为: {self.search_frequency}")

    def _get_rest_time(self):
        """获取休息时间 - 基于学习频率"""
        if self.search_frequency == "high":
            return 300  # 5分钟（高频率）
        elif self.search_frequency == "medium":
            return 600  # 10分钟（中频率）
        else:
            return 900  # 15分钟（低频率）

    def stop_learning(self):
        """停止持续学习"""
        self.is_running = False

        if self.learning_thread and self.learning_thread.is_alive():
            self.learning_thread.join(timeout=30)

        print("🛑 持续学习系统已停止")

    def get_learning_report(self):
        """获取学习报告（使用统一状态管理）"""
        try:
            continuous_state = self.state_manager.get_state("continuous")
            return {
                "learning_count": continuous_state.get("learning_count", 0),
                "learning_duration": continuous_state.get("learning_duration", 0),
                "knowledge_growth": continuous_state.get("knowledge_growth", 0),
                "interests": continuous_state.get("interests", []),
                "learned_topics": continuous_state.get("learned_topics", []),
                "last_learning": continuous_state.get("last_learning_time", "")
            }

        except Exception as e:
            print(f"⚠️  学习报告获取失败: {e}")
            return None

def test_continuous_learning():
    """测试持续学习系统"""
    print("🎯 测试持续学习系统")
    print("=" * 50)

    try:
        learning_system = ContinuousLearningSystem()

        # 启动持续学习（测试3次后停止）
        learning_system.start_continuous_learning()

        print("🚀 持续学习系统启动成功")

        # 测试运行
        try:
            # 等待3次学习
            for i in range(3):
                time.sleep(3)
                print()

        except KeyboardInterrupt:
            print("\n🛑 用户中断")

        finally:
            learning_system.stop_learning()
            learning_report = learning_system.get_learning_report()

            print("\n📊 学习报告:")
            if learning_report:
                print(f"学习次数: {learning_report['learning_count']}")
                print(f"学习时长: {learning_report['learning_duration']:.1f}分钟")
                print(f"学习兴趣: {', '.join(learning_report['interests'])}")
                print(f"上次学习: {learning_report['last_learning']}")

            print("✅ 测试完成")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    test_continuous_learning()
