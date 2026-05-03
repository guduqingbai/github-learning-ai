#!/usr/bin/env python3
"""
🧠 爬虫学习桥接器 — 爬完就学，好的资料深度学
每次爬虫抓取完成后自动评估内容价值，触发深度学习
"""

import json
import time
import ssl
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class CrawlerLearningBridge:
    """连接爬虫输出和学习系统的桥梁"""

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.learn_log = self.data_dir / "deep_learning_log.json"
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; LearningBot/1.0)"}
        self.ctx = ssl._create_unverified_context()

    # ── 对外入口 ──

    def process_crawl_results(self, items: List[Dict]) -> Dict[str, Any]:
        """爬虫完成后调用：评估 → 学习 → 深挖"""
        if not items:
            return {"evaluated": 0, "learned": 0, "deep_dives": 0}

        # 1. 评估内容价值
        evaluated = self._evaluate_items(items)

        # 2. 普通学习：全部入库（爬虫已经做了，我们补充深度标记）
        self._tag_kb_depth(evaluated)

        # 3. 深度挖掘：高价值内容触发多角度搜索
        deep_dives = self._trigger_deep_learning(evaluated)

        self._log_session(evaluated, deep_dives)
        return {
            "evaluated": len(evaluated),
            "learned": sum(1 for e in evaluated if e["_depth"] >= 1),
            "deep_dives": len(deep_dives),
        }

    # ── 内容评估 ──

    def _evaluate_items(self, items: List[Dict]) -> List[Dict]:
        """评估内容价值，打深度标记"""
        for item in items:
            source = item.get("source", "")
            importance = item.get("importance", 0.5)
            title = item.get("title", "")
            content = item.get("content", "")

            # 基础分来自爬虫的 importance
            score = importance

            # 加分：内容详细程度
            if len(content) > 200:
                score += 0.1
            if len(content) > 500:
                score += 0.1

            # 加分：来源权重
            source_boost = {"GitHub": 0.05, "arXiv": 0.1, "Wikipedia": 0.05}
            score += source_boost.get(source, 0)

            # 加分：标题包含核心关键词（自思考/AI架构/元认知等）
            core_keywords = ["self", "thinking", "autonomous", "meta", "curiosity",
                            "cognitive", "architecture", "self-improving", "self-modifying",
                            "自我", "思考", "认知", "元学习", "好奇心", "自主"]
            if any(k in title.lower() for k in core_keywords):
                score += 0.15

            score = min(1.0, score)

            # 深度等级
            if score >= 0.7:
                depth = 2  # 深度挖掘
            elif score >= 0.45:
                depth = 1  # 普通学习
            else:
                depth = 0  # 仅存储，不额外学习

            item["_score"] = round(score, 3)
            item["_depth"] = depth

        return items

    def _tag_kb_depth(self, evaluated: List[Dict]):
        """在知识库中标记深度等级和项目相关性"""
        project_keywords = ["self_thinking", "thinking_daemon", "self_scanner",
                            "curiosity", "cognition", "modification", "self_heal"]

        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            all_k = kb.get_all_knowledge()

            updated = 0
            for item in evaluated:
                topic = item.get("title", "")
                depth = item.get("_depth", 0)
                score = item.get("_score", 0)
                content = item.get("content", "") or ""
                if not topic:
                    continue

                # 计算项目相关性
                title_lower = topic.lower()
                content_lower = content.lower()
                if any(kw in title_lower for kw in project_keywords):
                    relevance = "high"
                elif any(kw in content_lower for kw in ["ai", "ml", "learning", "cognition", "architecture"]):
                    relevance = "medium"
                else:
                    relevance = "low"

                # 找到对应知识条目，补充深度元数据和相关性
                for entry in all_k:
                    if entry.get("topic") == topic:
                        if "learning_depth" not in entry:
                            entry["learning_depth"] = depth
                            entry["content_score"] = score
                            entry["relevance_to_project"] = relevance
                            updated += 1
                        break

            if updated > 0:
                self._log(f"📊 标记 {updated} 条知识的深度等级和项目相关性")
        except Exception as e:
            self._log(f"⚠️ 深度标记失败: {e}")

    # ── 深度学习触发 ──

    def _trigger_deep_learning(self, evaluated: List[Dict]) -> List[str]:
        """对高价值内容触发多角度深度搜索"""
        deep_items = [e for e in evaluated if e["_depth"] >= 2]
        if not deep_items:
            return []

        deep_dives = []
        for item in deep_items:
            title = item.get("title", "")
            keywords = item.get("keywords", [])

            # 从标题提取核心概念
            core_concept = self._extract_concept(title)

            # 为这个概念生成 3 个深入搜索方向
            search_queries = [
                f"{core_concept} architecture design",
                f"{core_concept} implementation guide",
                f"{core_concept} best practices 2026",
            ]

            # 如果有原始关键词，补充进去
            for kw in keywords[:2]:
                search_queries.append(f"{kw} {core_concept}")

            # 执行深度搜索（查 GitHub + 在线资源）
            results = []
            for query in search_queries[:4]:
                r = self._deep_search(query)
                results.extend(r)
                time.sleep(1)

            # 保存深度挖掘的结果
            if results:
                self._save_deep_results(core_concept, results)
                deep_dives.append(core_concept)
                self._log(f"🔬 深度挖掘 [{core_concept}]: 获取 {len(results)} 条进阶资料")

        return deep_dives

    def _extract_concept(self, title: str) -> str:
        """从标题提取核心概念"""
        # 去除常见前缀
        for prefix in ["[论文]", "[GitHub]", "arXiv:", "HN:"]:
            title = title.replace(prefix, "")

        # 取标题前半部分的核心词
        parts = title.split(":")
        core = parts[0].strip() if len(parts) > 1 else title.strip()

        # 如果标题太长，缩短
        words = core.split()[:5]
        return " ".join(words) if words else title[:50]

    def _deep_search(self, query: str) -> List[Dict]:
        """执行单次深度搜索"""
        results = []
        try:
            url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&per_page=3"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10, context=self.ctx) as resp:
                data = json.loads(resp.read().decode())
                for repo in data.get("items", [])[:3]:
                    results.append({
                        "title": repo["full_name"],
                        "content": repo.get("description", "") or "暂无描述",
                        "source": "GitHub深度学习",
                        "importance": min(1.0, repo.get("stargazers_count", 0) / 5000 + 0.5),
                        "link": repo["html_url"],
                        "keywords": [query],
                    })
        except Exception:
            pass

        # 如果 GitHub 没结果，尝试 arxiv
        if not results:
            try:
                url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&sortBy=relevance&max_results=3"
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=15, context=self.ctx) as resp:
                    xml = resp.read().decode("utf-8")
                    import re
                    titles = re.findall(r"<title>(.*?)</title>", xml, re.DOTALL)
                    for i, t in enumerate(titles[1:4], 1):
                        results.append({
                            "title": t.strip().replace("\n", " ")[:200],
                            "content": f"arXiv深度学习: {query}",
                            "source": "arXiv深度学习",
                            "importance": 0.85,
                            "link": f"https://arxiv.org/search/?query={query}",
                            "keywords": [query],
                        })
                    time.sleep(3)
            except Exception:
                pass

        return results

    def _save_deep_results(self, concept: str, results: List[Dict]):
        """保存深度挖掘结果到知识库"""
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            count = 0
            for r in results:
                entry = {
                    "topic": f"[深度] {r['title']}",
                    "category": "项目自身",
                    "content": f"深度学习结果 ({concept}): {r['content'][:300]}",
                    "source": r.get("source", "深度学习"),
                    "keywords": r.get("keywords", [concept]) + [concept, "深度学习"],
                    "references": [r.get("link", "")],
                    "importance": r.get("importance", 0.8),
                    "learning_time": datetime.now().isoformat(),
                    "learning_depth": 2,
                }
                if kb.add_knowledge(entry):
                    count += 1
            if count:
                self._log(f"📚 深度知识入库: {count} 条关于 '{concept}'")
        except Exception as e:
            self._log(f"⚠️ 深度知识保存失败: {e}")

    # ── 日志与持久化 ──

    def _log(self, msg: str):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [爬虫学习桥] {msg}")

    def _log_session(self, evaluated: List[Dict], deep_dives: List[str]):
        """记录学习会话"""
        logs = []
        if self.learn_log.exists():
            try:
                with open(self.learn_log, encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []

        logs.append({
            "timestamp": datetime.now().isoformat(),
            "items_evaluated": len(evaluated),
            "deep_dives": deep_dives,
            "depth_distribution": {
                "shallow": sum(1 for e in evaluated if e["_depth"] == 0),
                "normal": sum(1 for e in evaluated if e["_depth"] == 1),
                "deep": sum(1 for e in evaluated if e["_depth"] == 2),
            },
        })

        try:
            with open(self.learn_log, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


def process_crawler_results(items: List[Dict]) -> Dict[str, Any]:
    """便捷入口：处理爬虫结果"""
    bridge = CrawlerLearningBridge()
    return bridge.process_crawl_results(items)


if __name__ == "__main__":
    # 测试：模拟爬虫结果
    test_items = [
        {"title": "self-thinking-ai-system", "content": "A self-thinking AI system architecture with metacognition " * 10,
         "source": "GitHub", "importance": 0.8, "keywords": ["self thinking", "AI"]},
        {"title": "basic-python-tutorial", "content": "intro",
         "source": "Wikipedia", "importance": 0.3, "keywords": ["python"]},
    ]
    result = process_crawler_results(test_items)
    print(f"评估: {result['evaluated']}, 学习: {result['learned']}, 深挖: {result['deep_dives']}")
