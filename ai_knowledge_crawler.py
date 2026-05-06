#!/usr/bin/env python3

"""
🤖 AI知识自动爬虫 - 精爬版
专注 4 个高质量源：arXiv API + GitHub Topics + Papers With Code + Hacker News
过滤层 + 增量去重 + 礼貌爬取
"""
import os, sys, time, json, re
import threading, schedule
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 请求会话（连接复用 + 统一超时）
_http = requests.Session()
_http.headers.update({"User-Agent": "Mozilla/5.0 (compatible; LearningBot/1.0)"})
_http.headers.update({"From": "learning-bot@local"})  # 爬虫身份标识


class AIKnowledgeCrawler:
    """AI知识自动爬虫 — 精爬版"""

    # ─── 源可信度 ────────────────────────────────────────────────
    SOURCE_TRUST = {
        "arXiv": 0.9, "GitHub": 0.9, "定向爬虫": 0.8,
        "OpenAlex": 0.8, "Stack Overflow": 0.8,
        "CrossRef": 0.8, "Substack": 0.7,
        "Towards Data Science": 0.7,
        "Hacker News": 0.6,
    }
    DEFAULT_TRUST = 0.4

    # ─── 相关性关键词组 ────────────────────────────────────────────
    RELEVANCE_GROUPS = {
        "核心AI": [
            "artificial intelligence", "machine learning", "deep learning",
            "neural network", "nlp", "natural language processing",
            "llm", "large language model", "transformer", "attention mechanism",
            "gpt", "diffusion", "reinforcement learning", "foundation model",
            "computer vision", "data mining", "knowledge graph",
            "人工智能", "机器学习", "深度学习", "大语言模型",
        ],
        "自主系统": [
            "self-improv", "self improvement", "self-modif", "self-aware",
            "self-think", "self-evolv",
            "autonomous agent", "cognitive architecture", "cognitive", "cognition",
            "meta-cognit", "metacognit",
            "curiosity", "self-reflect", "self-correct", "recursive self",
            "自主", "自我改进", "元认知", "认知架构", "智能体", "agent",
        ],
        "工程实现": [
            "python", "algorithm", "data structure", "software architecture",
            "system design", "code generation", "programming", "api design",
            "算法", "数据结构", "软件架构", "系统设计", "编程",
        ],
    }

    def __init__(self):
        """__init__"""
        self.is_running = False
        self.crawl_thread = None
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.session_count = 0
        self.last_results = []
        self._log_buffer = []

        # 本次爬取去重（按标题前缀，不跨次持久化）
        self._seen_titles: set = set()

    def _is_new(self, title: str) -> bool:
        """爬取中去重：同一次爬取中标题前缀完全相同的跳过"""
        if not title:
            return False
        key = title[:80].lower().strip()
        if key in self._seen_titles:
            return False
        self._seen_titles.add(key)
        return True

    # ─── 日志 ────────────────────────────────────────────────────
    def log(self, msg):
        """log"""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        self._log_buffer.append(line + "\n")
        if len(self._log_buffer) >= 10:
            self._flush_log()

    def _flush_log(self):
        """_flush_log"""
        if not self._log_buffer:
            return
        log_file = self.data_dir / "ai_knowledge_crawler.log"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.writelines(self._log_buffer)
        finally:
            self._log_buffer.clear()

    # ─── 通用工具 ────────────────────────────────────────────────
    @staticmethod
    def _rate_limit(delay: float = 2.5):
        """礼貌爬取间隔"""
        time.sleep(delay)

    def _fetch(self, url: str, timeout: int = 30) -> str:
        """GET 请求，失败返回空字符串"""
        try:
            r = _http.get(url, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            self.log(f"⚠️ 请求失败: {url[:80]} → {e}")
            return ""

    # ─── 1. arXiv API（最高优先级）───────────────────────────────
    def crawl_arxiv(self) -> List[Dict]:
        """arXiv API 抓取自主系统和 AI Agent 相关论文"""
        queries = [
            # 标题搜索（精度高）
            'ti:autonomous+agent+AND+cat:cs.AI',
            'ti:self-improving+AND+cat:cs.AI',
            'ti:metacognition+AND+cat:cs.AI',
            'ti:cognitive+architecture+AND+cat:cs.AI',
            'ti:large+language+model+agent',
            # 能力/技能方向
            'ti:tool+use+AND+cat:cs.AI',
            'ti:retrieval+augmented+AND+cat:cs.AI',
            'ti:agent+framework+AND+cat:cs.AI',
            'ti:prompt+engineering+AND+cat:cs.AI',
            'ti:reinforcement+learning+from+human+feedback+AND+cat:cs.AI',
        ]
        results = []
        for q in queries:
            body = self._fetch(
                f"http://export.arxiv.org/api/query"
                f"?search_query={q}&start=0&max_results=10"
                f"&sortBy=submittedDate&sortOrder=descending",
                timeout=30)
            if not body:
                self._rate_limit(3)
                continue

            soup = BeautifulSoup(body, "xml" if "lxml" in str(type(body)) else "html.parser")
            entries = soup.find_all("entry") if soup.find("entry") else []
            # 退回到正则解析（BeautifulSoup 的 XML 解析可能不如正则可靠）
            if not entries:
                entries = re.findall(r'<entry>(.*?)</entry>', body, re.DOTALL)
                entries = [BeautifulSoup(e, "html.parser") for e in entries]

            for entry in entries:
                title = entry.find("title")
                title = (title.get_text(strip=True) if title else "")[:200]
                title = re.sub(r'\s+', ' ', title).strip()

                summary = entry.find("summary")
                summary = (summary.get_text(strip=True) if summary else "")[:400]
                summary = re.sub(r'\s+', ' ', summary).strip()

                eid = entry.find("id")
                url = eid.get_text(strip=True) if eid else ""

                cats = entry.find_all("category")
                cat_terms = [c.get("term", "") for c in cats if c.get("term")]

                if not title:
                    continue
                if not self._is_new(title):
                    continue

                results.append({
                    "title": title,
                    "content": summary,
                    "source": "arXiv",
                    "importance": 0.85,
                    "link": url,
                    "keywords": cat_terms + [q.split(":")[0] for q in q.split("+AND+")],
                })

            self.log(f"  📄 arXiv [{q.split('&')[0][:50]}]: {len(results)} 条")
            self._rate_limit(3.5)  # arXiv 要求至少 3 秒

        self.log(f"  ✅ arXiv 总计: {len(results)} 条论文")
        return results

    # ─── 2. GitHub API ───────────────────────────────────────────
    def crawl_github(self) -> List[Dict]:
        """GitHub API 搜索 AI 能力/技能相关仓库"""
        results = []
        gh_headers = {"Accept": "application/vnd.github.v3+json"}
        queries = [
            # 研究方向
            ("topic:autonomous-agents", "autonomous-agents"),
            ("topic:self-improving-ai", "self-improving-ai"),
            ("topic:cognitive-architecture", "cognitive-architecture"),
            ("topic:ai-agents", "ai-agents"),
            ("topic:meta-learning", "meta-learning"),
            ("self-improving+AI+agent", "self-improving"),
            ("metacognition+framework", "metacognition"),
            # 能力/技能（AI 工具链）
            ("topic:langchain", "langchain"),
            ("topic:rag", "rag"),
            ("topic:embeddings", "embeddings"),
            ("topic:ai-agent", "ai-agent"),
            ("topic:function-calling", "function-calling"),
            ("topic:large-language-model", "llm"),
            ("topic:prompt-engineering", "prompt-engineering"),
            ("topic:vector-database", "vector-database"),
        ]
        for q, label in queries:
            body = self._fetch(
                f"https://api.github.com/search/repositories"
                f"?q={requests.utils.quote(q)}&sort=stars&per_page=15",
                timeout=15)
            if not body:
                self._rate_limit(2)
                continue
            try:
                data = json.loads(body)
                for repo in data.get("items", [])[:15]:
                    full_name = repo["full_name"]
                    link = repo["html_url"]
                    if not self._is_new(full_name):
                        continue
                    results.append({
                        "title": full_name,
                        "content": (repo.get("description") or "暂无描述")[:400],
                        "source": "GitHub",
                        "importance": min(1.0, repo.get("stargazers_count", 0) / 5000 + 0.3),
                        "link": link,
                        "keywords": [label],
                    })
            except (json.JSONDecodeError, KeyError) as e:
                self.log(f"  ⚠️ GitHub API 解析失败 [{q}]: {e}")

            self.log(f"  🌐 GitHub [{label}]: {len(results)} 条")
            self._rate_limit(2)

        self.log(f"  ✅ GitHub 总计: {len(results)} 条仓库")
        return results

    # ─── 3. OpenAlex（开放学术索引）─────────────────────────────
    def crawl_paperswithcode(self) -> List[Dict]:
        """OpenAlex API 搜索自主系统/元认知相关论文（开源，无需 Key）"""
        results = []
        queries = [
            ("cognitive architecture autonomous agent", "认知架构"),
            ("self-improving AI system", "自改进系统"),
            ("metacognition artificial intelligence", "元认知AI"),
            ("LLM agent reasoning", "LLM智能体"),
            ("curiosity driven learning agent", "好奇驱动"),
            # 能力/技能方向
            ("prompt engineering techniques", "提示工程"),
            ("tool use AI agent", "工具使用"),
            ("AI alignment safety", "AI对齐"),
            ("retrieval augmented generation", "RAG"),
            ("reinforcement learning from human feedback", "RLHF"),
        ]
        for q, label in queries:
            url = (f"https://api.openalex.org/works"
                   f"?search={requests.utils.quote(q)}"
                   f"&sort=cited_by_count:desc"
                   f"&per_page=10"
                   f"&select=id,title,abstract_inverted_index,authorships,doi,publication_date,cited_by_count")
            body = self._fetch(url, timeout=15)
            if not body:
                self._rate_limit(2)
                continue

            try:
                data = json.loads(body)
                for work in data.get("results", [])[:10]:
                    title = (work.get("title") or "")[:200]
                    doi = work.get("doi") or work.get("id", "")
                    link = doi if doi.startswith("http") else f"https://doi.org/{doi}" if doi else url

                    if not self._is_new(title):
                        continue

                    # OpenAlex 用 inverted index 存摘要
                    abstract_idx = work.get("abstract_inverted_index")
                    abstract = ""
                    if abstract_idx:
                        word_positions = []
                        for word, positions in abstract_idx.items():
                            for pos in positions:
                                word_positions.append((pos, word))
                        word_positions.sort()
                        abstract = " ".join(w for _, w in word_positions)[:400]

                    results.append({
                        "title": title,
                        "content": abstract or "OpenAlex 学术论文",
                        "source": "OpenAlex",
                        "importance": min(0.9, 0.5 + (work.get("cited_by_count", 0) or 0) / 100),
                        "link": link,
                        "keywords": [label, "学术论文"],
                    })
            except (json.JSONDecodeError, KeyError) as e:
                self.log(f"  ⚠️ OpenAlex 解析失败 [{q}]: {e}")

            self.log(f"  📝 OpenAlex [{label}]: {len(results)} 条")
            self._rate_limit(2.5)

        self.log(f"  ✅ OpenAlex 总计: {len(results)} 条论文")
        return results

    # ─── 4. Hacker News (Algolia API) ────────────────────────────
    def crawl_hackernews(self) -> List[Dict]:
        """通过 Algolia API 搜索 HN 上 AI Agent 相关讨论"""
        results = []
        queries = [
            "AI agent", "autonomous agent", "self-improving AI",
            "meta-cognition", "LLM agent",
            "prompt engineering", "RAG", "AI tool use",
        ]
        for q in queries:
            url = (f"https://hn.algolia.com/api/v1/search"
                   f"?tags=story&query={requests.utils.quote(q)}"
                   f"&hitsPerPage=10")
            body = self._fetch(url, timeout=15)
            if not body:
                self._rate_limit(2.5)
                continue

            try:
                data = json.loads(body)
                for hit in data.get("hits", [])[:10]:
                    title = hit.get("title", "")
                    link = hit.get("url") or hit.get("story_url") or \
                           f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
                    if not title:
                        continue
                    if not self._is_new(title):
                        continue
                    points = hit.get("points", 0) or 0
                    results.append({
                        "title": title,
                        "content": hit.get("story_text", "") or f"Hacker News 讨论: {q}",
                        "source": "Hacker News",
                        "importance": min(0.9, 0.5 + points / 200),
                        "link": link,
                        "keywords": [q],
                    })
            except json.JSONDecodeError:
                pass

            self._rate_limit(2.5)

        self.log(f"  ✅ Hacker News 总计: {len(results)} 条")
        return results

    # ─── 5. 定向任务队列 ────────────────────────────────────────
    def crawl_task_queue(self) -> List[Dict]:
        """读取自主学习任务队列，逐任务处理（保持不变）"""
        task_file = self.data_dir / "crawler_tasks.json"
        if not task_file.exists():
            return []

        with open(task_file, "r", encoding="utf-8") as f:
            tasks = json.load(f)

        if not tasks:
            return []

        limit = min(5, len(tasks))
        self.log(f"🎯 自主学习任务队列: 共{len(tasks)}个, 本次处理{limit}个")

        results = []
        for _ in range(limit):
            with open(task_file, "r", encoding="utf-8") as f:
                current = json.load(f)
            if not current:
                break

            task = current.pop(0)
            query = task["query"]
            domain = task.get("domain", "知识学习")
            self.log(f"   📌 定向抓取: [{domain}] {query}")

            try:
                body = self._fetch(
                    f"https://api.github.com/search/repositories"
                    f"?q={requests.utils.quote(query)}&sort=stars&per_page=3",
                    timeout=15)
                if body:
                    data = json.loads(body)
                    for repo in data.get("items", [])[:3]:
                        link = repo["html_url"]
                        full_name = repo["full_name"]
                        if not self._is_new(full_name):
                            continue
                        results.append({
                            "title": f"[{domain}] {full_name}",
                            "content": (repo.get("description") or f"{query}相关项目")[:400],
                            "source": f"定向爬虫/{domain}",
                            "importance": min(1.0, repo.get("stargazers_count", 0) / 5000 + 0.5),
                            "link": link,
                            "keywords": [domain, query],
                        })

                if current:
                    with open(task_file, "w", encoding="utf-8") as f:
                        json.dump(current, f, ensure_ascii=False, indent=2)
                else:
                    task_file.unlink()
                    self.log("🎉 所有定向任务已完成！")
                self._rate_limit(2)
            except Exception as e:
                self.log(f"   ⚠️ 定向抓取失败 [{query}]: {e}")
                current.insert(0, task)
                with open(task_file, "w", encoding="utf-8") as f:
                    json.dump(current, f, ensure_ascii=False, indent=2)
                break

        if results:
            self.log(f"✅ 定向抓取: 获取 {len(results)} 条知识")
        return results

    # ─── 5. Stack Overflow ──────────────────────────────────────────
    def crawl_stackoverflow(self) -> List[Dict]:
        """Stack Exchange API 搜索 AI/ML 技术问答"""
        results = []
        tags = [
            "machine-learning", "deep-learning", "artificial-intelligence",
            "nlp", "large-language-model", "autonomous-agents",
            "langchain", "prompt-engineering", "rag",
        ]
        for tag in tags:
            url = (f"https://api.stackexchange.com/2.3/questions"
                   f"?tagged={tag}&pagesize=5&order=desc&sort=votes"
                   f"&site=stackoverflow&filter=withbody")
            body = self._fetch(url, timeout=15)
            if not body:
                self._rate_limit(2)
                continue
            try:
                data = json.loads(body)
                for q in data.get("items", [])[:5]:
                    title = q.get("title", "")
                    if not title or not self._is_new(title):
                        continue
                    link = q.get("link", "")
                    answer_count = q.get("answer_count", 0)
                    score = q.get("score", 0)
                    content = q.get("body", "")[:400]
                    content = re.sub(r'<[^>]+>', '', content).strip()[:400]
                    results.append({
                        "title": title,
                        "content": content or f"Stack Overflow ({tag} 标签)",
                        "source": "Stack Overflow",
                        "importance": min(0.9, 0.4 + score / 50 + answer_count / 20),
                        "link": link,
                        "keywords": [tag, "技术问答"],
                    })
            except (json.JSONDecodeError, KeyError) as e:
                self.log(f"  ⚠️ Stack Overflow 解析失败 [{tag}]: {e}")
            self._rate_limit(2)
        self.log(f"  ✅ Stack Overflow 总计: {len(results)} 条")
        return results

    # ─── 6. CrossRef（学术论文元数据）──────────────────────────────
    def crawl_crossref(self) -> List[Dict]:
        """CrossRef API 搜索 AI 相关学术论文"""
        results = []
        queries = [
            "autonomous agent artificial intelligence",
            "self-improving AI",
            "cognitive architecture metacognition",
            "large language model reasoning",
            "retrieval augmented generation",
        ]
        for q in queries:
            url = (f"https://api.crossref.org/works"
                   f"?query={requests.utils.quote(q)}"
                   f"&rows=10&select=DOI,title,abstract,author,container-title")
            body = self._fetch(url, timeout=15)
            if not body:
                self._rate_limit(2)
                continue
            try:
                data = json.loads(body)
                for item in data.get("message", {}).get("items", []):
                    title_list = item.get("title", [])
                    title = title_list[0] if title_list else ""
                    if not title or not self._is_new(title):
                        continue
                    doi = item.get("DOI", "")
                    link = f"https://doi.org/{doi}" if doi else ""
                    abstract = item.get("abstract", "")[:400] if item.get("abstract") else ""
                    abstract = re.sub(r'<[^>]+>', '', abstract).strip()[:400]
                    journal = item.get("container-title", [])
                    journal = journal[0] if journal else "学术期刊"
                    results.append({
                        "title": title,
                        "content": abstract or f"CrossRef: {journal}",
                        "source": "CrossRef",
                        "importance": 0.8,
                        "link": link or title,
                        "keywords": [q.split()[0], "学术论文"],
                    })
            except (json.JSONDecodeError, KeyError) as e:
                self.log(f"  ⚠️ CrossRef 解析失败 [{q}]: {e}")
            self._rate_limit(2)
        self.log(f"  ✅ CrossRef 总计: {len(results)} 条")
        return results

    # ─── 7. Substack ─────────────────────────────────────────────
    def crawl_substack(self) -> List[Dict]:
        """Substack API 爬取 AI 相关 newsletter 文章"""
        results = []
        pubs = [
            ("https://thealgorithmicbridge.com", "The Algorithmic Bridge"),
            ("https://www.oneusefulthing.org", "One Useful Thing"),
            ("https://lastweekin.ai", "Last Week in AI"),
            ("https://www.digitalnative.tech", "Digital Native"),
            ("https://magazine.sebastianraschka.com", "Ahead of AI"),
        ]
        for pub_url, pub_name in pubs:
            try:
                r = _http.get(f"{pub_url}/api/v1/archive", timeout=10)
                if r.status_code != 200:
                    continue
                items = r.json()
                if not isinstance(items, list):
                    continue
                for post in items[:10]:
                    title = post.get("title", "")
                    if not title or not self._is_new(title):
                        continue
                    desc = post.get("description") or post.get("subtitle") or ""
                    body = post.get("truncated_body_text", "")[:300]
                    content = (desc + " " + body).strip()[:400]
                    link = post.get("canonical_url") or f"{pub_url}/p/{post.get('slug', '')}"
                    results.append({
                        "title": title,
                        "content": content or f"Substack: {pub_name}",
                        "source": f"Substack/{pub_name}",
                        "importance": 0.8,
                        "link": link,
                        "keywords": [pub_name, "newsletter"],
                    })
            except Exception:
                continue
        self.log(f"  ✅ Substack 总计: {len(results)} 条")
        return results

    # ─── 8. Towards Data Science（RSS Feed）────────────────────────
    def crawl_tds(self) -> List[Dict]:
        """Towards Data Science RSS Feed — Medium 上最高质量的 AI 技术博客"""
        results = []
        tds_url = "https://towardsdatascience.com/feed"
        body = self._fetch(tds_url, timeout=20)
        if not body:
            self.log("  ⚠️ TDS RSS 不可用")
            return results

        try:
            soup = BeautifulSoup(body, "xml" if "lxml" in str(type(body)) else "html.parser")
            items = soup.find_all("item") if soup.find("item") else []
            if not items:
                # 退回到正则+RSS 标签解析
                items = re.findall(r'<item>(.*?)</item>', body, re.DOTALL)
                items = [BeautifulSoup(e, "html.parser") for e in items]

            for entry in items[:20]:
                title = entry.find("title")
                title = (title.get_text(strip=True) if title else "")[:200]
                if not title or not self._is_new(title):
                    continue

                desc = entry.find("description")
                content = (desc.get_text(strip=True) if desc else "")[:400]
                content = re.sub(r'<[^>]+>', '', content).strip()[:400]

                link = entry.find("link")
                url = link.get_text(strip=True) if link else ""

                creator = entry.find("dc:creator")
                author = creator.get_text(strip=True) if creator else ""

                cats = entry.find_all("category")
                keywords = []
                for c in cats:
                    kw = c.get_text(strip=True)
                    if kw and len(kw) < 50:
                        keywords.append(kw)

                results.append({
                    "title": title,
                    "content": content or f"Towards Data Science: {author}",
                    "source": f"Towards Data Science",
                    "importance": 0.8,
                    "link": url,
                    "keywords": keywords[:5] if keywords else ["数据科学", "AI实践"],
                })
        except Exception as e:
            self.log(f"  ⚠️ TDS 解析失败: {e}")

        self.log(f"  ✅ Towards Data Science 总计: {len(results)} 条")
        return results

    # ─── 相关性过滤 ────────────────────────────────────────────
    def _is_relevant(self, item: Dict) -> bool:
        """_is_relevant"""
        if not item.get("content"):
            return False

        text = (item.get("title") or "") + " " + (item.get("content") or "")
        text_lower = text.lower()

        matched_groups = []
        for group, keywords in self.RELEVANCE_GROUPS.items():
            if any(kw in text_lower for kw in keywords):
                matched_groups.append(group)

        src = item.get("source", "")
        trust = self.DEFAULT_TRUST
        for known_src, t in self.SOURCE_TRUST.items():
            if known_src in src:
                trust = t
                break

        # 最高信任源（arXiv/GitHub）：搜索带领域限定（cat:cs.AI/topic标签），直接信任
        if trust >= 0.9:
            return True

        # 高信任源（OpenAlex/定向爬虫）：需要至少匹配一个关键词组
        if trust >= 0.7:
            return len(matched_groups) >= 1

        # 中信任源（Hacker News）：匹配到至少一个关键词组才保留
        if trust >= 0.4:
            return len(matched_groups) >= 1

        return False

    # ─── 自动分类 ────────────────────────────────────────────────
    CATEGORY_MAP = [
        (["元认知", "自主", "self-improv", "self-modif", "meta-cognit",
          "metacognit", "cognitive architecture", "curiosity", "self-aware",
          "autonomous agent"],
         "认知架构"),
        (["artificial intelligence", "machine learning", "deep learning",
          "neural network", "nlp", "llm", "transformer", "gpt", "diffusion",
          "reinforcement learning", "foundation model", "attention mechanism",
          "人工智能", "机器学习", "深度学习", "大语言模型"],
         "人工智能"),
        (["python", "algorithm", "data structure", "programming", "coding",
          "software architecture", "system design",
          "算法", "数据结构", "软件架构", "系统设计", "编程"],
         "工程实现"),
    ]

    def _assign_category(self, item: Dict) -> str:
        """_assign_category"""
        text = (item.get("title") or "") + " " + (item.get("content") or "")
        text_lower = text.lower()

        for keywords, cat in self.CATEGORY_MAP:
            for kw in keywords:
                if kw in text_lower:
                    return cat
        return "人工智能"

    # ─── 保存到知识库 ──────────────────────────────────────────
    def save_knowledge(self, items: List[Dict]):
        """save_knowledge"""
        if not items:
            self.log("📭 没有新知识需要保存")
            return
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()

            total = len(items)
            discarded_by_src = {}

            filtered = []
            for item in items:
                if self._is_relevant(item):
                    filtered.append(item)
                else:
                    src = item.get("source", "未知")
                    discarded_by_src[src] = discarded_by_src.get(src, 0) + 1

            if discarded_by_src:
                detail = ", ".join(f"{s}: {n}" for s, n in sorted(discarded_by_src.items()))
                self.log(f"🗑️ 丢弃 {total - len(filtered)}/{total} 条 ({detail})")

            if not filtered:
                self.log("📭 过滤后无有效知识")
                return

            count = 0
            for item in filtered:
                entry = {
                    "topic": item["title"],
                    "category": self._assign_category(item),
                    "content": item["content"],
                    "source": item["source"],
                    "keywords": item.get("keywords", ["AI"]),
                    "references": [item.get("link", "")],
                    "importance": item.get("importance", 0.5),
                    "learning_time": datetime.now().isoformat(),
                }
                kb.learn_from_experience(entry)
                count += 1
            self.log(f"✅ 保存 {count} 条知识 (过滤前{total}条)")
        except Exception as e:
            self.log(f"❌ 保存知识失败: {e}")

    # ─── 执行完整爬取 ──────────────────────────────────────────
    def crawl_all(self):
        """crawl_all"""
        self.session_count += 1
        self.log(f"🚀 [第{self.session_count}次] 开始爬取")
        print("=" * 60)

        all_items = []

        self.log("📄 正在爬取 arXiv 论文...")
        all_items.extend(self.crawl_arxiv())

        self.log("🌐 正在爬取 GitHub 仓库...")
        all_items.extend(self.crawl_github())

        self.log("📚 正在爬取 OpenAlex 学术论文...")
        all_items.extend(self.crawl_paperswithcode())

        self.log("📰 正在爬取 Hacker News...")
        all_items.extend(self.crawl_hackernews())

        self.log("📋 正在爬取 Stack Overflow...")
        all_items.extend(self.crawl_stackoverflow())

        self.log("📇 正在爬取 CrossRef 学术论文...")
        all_items.extend(self.crawl_crossref())

        self.log("📬 正在爬取 Substack AI 文章...")
        all_items.extend(self.crawl_substack())

        self.log("📝 正在爬取 Towards Data Science...")
        all_items.extend(self.crawl_tds())

        self.log("🎯 正在执行定向任务...")
        all_items.extend(self.crawl_task_queue())

        # 去重（标题前缀）
        seen = set()
        unique = []
        for item in all_items:
            key = item["title"][:60]
            if key not in seen:
                seen.add(key)
                unique.append(item)

        self.log(f"\n📊 汇总:")
        sources = {}
        for item in unique:
            src = item["source"]
            sources[src] = sources.get(src, 0) + 1
        for src, cnt in sorted(sources.items()):
            self.log(f"   {src}: {cnt} 条")
        self.log(f"   共计: {len(unique)} 条 (去重后)")

        self.save_knowledge(unique)
        self.last_results = unique
        self._flush_log()
        self.log(f"✅ [第{self.session_count}次] 爬取完成\n")

    # ─── 调度器 ────────────────────────────────────────────────
    def run_scheduler(self):
        """run_scheduler"""
        schedule.every(2).hours.at(":00").do(self.crawl_all)
        self.log("⏰ 调度器已启动，每2小时整点执行")
        self.crawl_all()
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)

    def start(self):
        """start"""
        if self.is_running:
            self.log("⚠️ 爬虫已在运行")
            return
        self.is_running = True
        self.crawl_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.crawl_thread.start()
        self.log("✅ 爬虫启动成功 (精爬版)")

    def stop(self):
        """stop"""
        self.log("🛑 正在停止爬虫...")
        self.is_running = False
        if self.crawl_thread:
            self.crawl_thread.join(timeout=10)
        self._flush_log()
        self.log("✅ 爬虫已停止")

    def get_status(self) -> Dict:
        """get_status"""
        log_file = self.data_dir / "ai_knowledge_crawler.log"
        recent = []
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-15:]
                    recent = [l.strip() for l in lines if l.strip()]
            except Exception:
                pass
        return {
            "running": self.is_running,
            "sessions": self.session_count,
            "sources": ["arXiv", "GitHub", "OpenAlex", "Hacker News", "Stack Overflow", "CrossRef", "Substack", "TDS"],
            "seen_urls": len(self.seen_urls),
            "recent_logs": recent,
        }


def main():
    """main"""
    print("🤖 AI知识自动爬虫 (精爬版)")
    print("=" * 60)
    print("数据源: arXiv | GitHub | OpenAlex | Stack Overflow | CrossRef | Substack | TDS | Hacker News")
    print("调度: 每2小时整点执行\n")

    crawler = AIKnowledgeCrawler()
    try:
        crawler.start()
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        crawler.stop()


if __name__ == "__main__":
    main()
