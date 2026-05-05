#!/usr/bin/env python3
"""
🌐 定向爬取调度器 — 聚焦 AI 架构/自主 Agent 领域

定向而非泛爬：来源限定为 arXiv、GitHub、用户指定源。
爬取频率每日，与修改频率分离（修改由价值评估控制）。
"""
import json
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional


@dataclass
class CrawlSource:
    """一个可爬取的数据来源"""
    name: str                     # 唯一标识，如 "arxiv_ai_agents"
    url_template: str             # URL 模板，{query} 会被替换
    query_template: str           # 查询参数模板
    interval_hours: int = 24      # 爬取间隔
    last_crawled: str = ""        # ISO 时间
    priority: int = 5             # 1-10，越高越重要
    enabled: bool = True


# 默认爬取来源
DEFAULT_SOURCES = [
    CrawlSource(
        name="arxiv_ai_agents",
        url_template="http://export.arxiv.org/api/query?search_query=all:{query}&sortBy=relevance&sortOrder=descending&max_results=5",
        query_template="cat:cs.AI+AND+abs:autonomous+agent",
        interval_hours=24, priority=9,
    ),
    CrawlSource(
        name="arxiv_self_improving",
        url_template="http://export.arxiv.org/api/query?search_query=all:{query}&sortBy=relevance&sortOrder=descending&max_results=5",
        query_template="cat:cs.AI+AND+abs:self-improving",
        interval_hours=24, priority=8,
    ),
    CrawlSource(
        name="arxiv_metacognition",
        url_template="http://export.arxiv.org/api/query?search_query=all:{query}&sortBy=relevance&sortOrder=descending&max_results=5",
        query_template="cat:cs.AI+AND+abs:metacognition",
        interval_hours=24, priority=7,
    ),
    CrawlSource(
        name="github_autonomous",
        url_template="https://api.github.com/search/repositories?q=topic:{query}&sort=stars&order=desc&per_page=5",
        query_template="autonomous-agents",
        interval_hours=48, priority=7,
    ),
]


class DirectedCrawler:
    """
    定向爬取调度器。

    专注于 AI 架构/自主 Agent 领域的定向爬取，
    复用 ContentFetcher 和 AnswerSynthesizer 进行提取。
    """

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self._sources_file = self.data_dir / "crawl_sources.json"
        self._sources: List[CrawlSource] = []
        self._load_sources()
        self._fetcher = None   # lazy: ContentFetcher
        self._synthesizer = None  # lazy: AnswerSynthesizer

    # ── Hook 注册 ──

    def register_hooks(self, agent) -> None:
        """注册 POST_SCAN hook，用于每日触发爬取"""
        try:
            agent.register_hook("post_scan", self._on_post_scan,
                                name="directed_crawl_on_scan", priority=15)
        except Exception:
            pass

    def _on_post_scan(self, agent, **kw) -> None:
        """POST_SCAN hook：检查 feature flag，执行到期的爬取任务"""
        try:
            if not agent._check_feature("capability_learning"):
                return
            results = self.crawl_ai_archives()
            if not results:
                return
            concepts = []
            for r in results:
                c = self.extract_capability_concepts(r)
                if c:
                    concepts.append(c)
            if concepts:
                self.store_concepts(agent, concepts)
        except Exception:
            pass

    # ── 爬取调度 ──

    def crawl_ai_archives(self) -> List[Dict]:
        """遍历所有到期的来源，执行爬取。返回原始结果列表。"""
        results = []
        due_sources = self._get_due_sources()

        if not due_sources:
            return results

        for source in due_sources:
            try:
                urls = self._build_urls(source)
                for url in urls:
                    resp = self._fetch_url(url)
                    if resp:
                        parsed = self._parse_response(source.name, resp)
                        results.extend(parsed)
                    time.sleep(1)  # 礼貌延迟
                source.last_crawled = datetime.now().isoformat()
            except Exception:
                pass

        self._save_sources()
        return results

    def add_custom_source(self, name: str, url_template: str,
                           query_template: str,
                           interval_hours: int = 24,
                           priority: int = 5) -> None:
        """添加用户自定义爬取源"""
        # 去重
        self._sources = [s for s in self._sources if s.name != name]
        self._sources.append(CrawlSource(
            name=name, url_template=url_template,
            query_template=query_template,
            interval_hours=interval_hours, priority=priority,
        ))
        self._save_sources()

    # ── 概念提取 ──

    def extract_capability_concepts(self, result: Dict) -> Optional[Dict]:
        """
        从原始爬取结果提取"能力描述"。
        返回 {topic, description, keywords, source_url} 或 None
        """
        if not result or not result.get("title"):
            return None
        return {
            "topic": result.get("title", "未知")[:100],
            "description": (result.get("summary") or result.get("description") or "")[:500],
            "keywords": self._extract_keywords(result),
            "source_url": result.get("url", ""),
            "source_name": result.get("source_name", "unknown"),
        }

    def store_concepts(self, agent, concepts: List[Dict]) -> int:
        """将概念存入知识库，category='能力参考'。返回存入数量。"""
        stored = 0
        try:
            for c in concepts:
                kb_entry = {
                    "topic": c["topic"],
                    "content": c["description"],
                    "category": "能力参考",
                    "keywords": c["keywords"],
                    "importance": 0.7,
                    "source": c.get("source_name", "web"),
                    "learning_depth": 1,
                    "content_score": 0.6,
                }
                try:
                    from knowledge_base import KnowledgeBase
                    kb = KnowledgeBase()
                    kb.learn_from_experience([kb_entry])
                    stored += 1
                except Exception:
                    pass
        except Exception:
            pass
        return stored

    # ── 内部方法 ──

    def _get_fetcher(self):
        """惰性加载 ContentFetcher"""
        if self._fetcher is None:
            try:
                from web_researcher import ContentFetcher
                self._fetcher = ContentFetcher()
            except Exception:
                self._fetcher = object()  # 占位
        return self._fetcher

    def _fetch_url(self, url: str) -> Optional[str]:
        """HTTP GET 返回文本内容"""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Week8ThinkingDaemon/1.0 (autonomous research)",
                    "Accept": "application/json, text/plain, text/xml, */*",
                })
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception:
            return None

    def _build_urls(self, source: CrawlSource) -> List[str]:
        """根据来源生成要请求的具体 URL 列表"""
        query = source.query_template.format(query=source.query_template)
        url = source.url_template.replace("{query}", urllib.parse.quote(query))
        return [url]

    def _parse_response(self, source_name: str, text: str) -> List[Dict]:
        """根据来源名称解析响应"""
        if "arxiv" in source_name:
            return self._parse_arxiv_xml(text, source_name)
        elif "github" in source_name:
            return self._parse_github_json(text, source_name)
        return []

    @staticmethod
    def _parse_arxiv_xml(xml_text: str, source_name: str) -> List[Dict]:
        """解析 arXiv Atom XML 响应"""
        results = []
        try:
            ns = {"atom": "http://www.w3.org/2005/Atom",
                  "arxiv": "http://arxiv.org/schemas/atom"}
            root = ET.fromstring(xml_text)
            for entry in root.findall("atom:entry", ns):
                title = entry.findtext("atom:title", "", ns).strip()
                summary = entry.findtext("atom:summary", "", ns).strip()
                id_url = entry.findtext("atom:id", "", ns)
                # 清理换行和多余空格
                summary = " ".join(summary.split())[:800]
                results.append({
                    "title": title[:200],
                    "summary": summary,
                    "url": id_url,
                    "source_name": source_name,
                    "source_type": "arxiv",
                })
        except Exception:
            pass
        return results

    @staticmethod
    def _parse_github_json(json_text: str, source_name: str) -> List[Dict]:
        """解析 GitHub Search API JSON 响应"""
        results = []
        try:
            data = json.loads(json_text)
            items = data.get("items", [])
            for item in items[:5]:
                results.append({
                    "title": item.get("full_name", item.get("name", "未知")),
                    "description": item.get("description") or item.get("topics", []),
                    "url": item.get("html_url", ""),
                    "source_name": source_name,
                    "source_type": "github",
                    "stars": item.get("stargazers_count", 0),
                })
        except Exception:
            pass
        return results

    @staticmethod
    def _extract_keywords(result: Dict) -> List[str]:
        """从结果中提取关键词"""
        kw = set()
        title = result.get("title", "")
        summary = result.get("summary") or result.get("description", "")
        for word in (title + " " + str(summary)).lower().split():
            word = word.strip(",:;.()[]{}").strip()
            if len(word) > 3 and word.isascii():
                kw.add(word)
        return sorted(kw)[:15]

    def _get_due_sources(self) -> List[CrawlSource]:
        """返回到期待爬的来源列表"""
        now = datetime.now()
        due = []
        for s in self._sources:
            if not s.enabled:
                continue
            if not s.last_crawled:
                due.append(s)
                continue
            try:
                last = datetime.fromisoformat(s.last_crawled)
                if now - last >= timedelta(hours=s.interval_hours):
                    due.append(s)
            except Exception:
                due.append(s)
        return due

    def _load_sources(self):
        """从文件加载来源配置"""
        if not self._sources_file.exists():
            self._sources = DEFAULT_SOURCES
            self._save_sources()
            return
        try:
            data = json.loads(self._sources_file.read_text(encoding="utf-8"))
            items = data if isinstance(data, list) else data.get("sources", [])
            self._sources = []
            for item in items:
                self._sources.append(CrawlSource(
                    name=item.get("name", "未知"),
                    url_template=item.get("url_template", ""),
                    query_template=item.get("query_template", ""),
                    interval_hours=item.get("interval_hours", 24),
                    last_crawled=item.get("last_crawled", ""),
                    priority=item.get("priority", 5),
                    enabled=item.get("enabled", True),
                ))
        except Exception:
            self._sources = DEFAULT_SOURCES

    def _save_sources(self):
        """持久化来源配置"""
        try:
            data = {
                "sources": [
                    {
                        "name": s.name,
                        "url_template": s.url_template,
                        "query_template": s.query_template,
                        "interval_hours": s.interval_hours,
                        "last_crawled": s.last_crawled,
                        "priority": s.priority,
                        "enabled": s.enabled,
                    }
                    for s in self._sources
                ],
                "updated_at": datetime.now().isoformat(),
            }
            self._sources_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass


def main():
    """测试 DirectedCrawler 基础功能"""
    print("=" * 50)
    print("  DirectedCrawler 测试")
    print("=" * 50)

    crawler = DirectedCrawler()
    print(f"\n1. 默认来源数: {len(crawler._sources)}")
    for s in crawler._sources:
        print(f"   [{s.name}] 间隔={s.interval_hours}h 优先级={s.priority}")

    print(f"\n2. 模拟概念提取...")
    sample = {
        "title": "Self-Improving Autonomous Agent with Metacognition",
        "summary": "A novel architecture for agents that can reflect on their own thinking process and improve their decision-making over time.",
        "url": "http://arxiv.org/abs/1234.56789",
        "source_name": "arxiv_test",
    }
    concept = crawler.extract_capability_concepts(sample)
    assert concept is not None
    print(f"   提取概念: {concept['topic']}")
    print(f"   关键词: {concept['keywords'][:5]}")

    print(f"\n3. 到期来源检测...")
    due = crawler._get_due_sources()
    print(f"   当前到期: {len(due)} 个")
    assert len(due) > 0, "首次运行所有来源都应到期"

    print(f"\n4. 添加自定义来源...")
    crawler.add_custom_source("test_source",
                               "https://example.com/api?q={query}",
                               "test+query",
                               interval_hours=12)
    assert any(s.name == "test_source" for s in crawler._sources)
    print(f"   自定义来源已添加")

    print("\n✅ DirectedCrawler 测试完成")
    return True


if __name__ == "__main__":
    main()
