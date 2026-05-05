#!/usr/bin/env python3
"""
Web Researcher — 多源搜索 + 网页内容提取 + 答案综合

零外部依赖，只使用标准库 urllib + re。
一个查询同时搜索 6 个来源，单源失败不影响其他。
"""

import json
import re
import time
import urllib.request
import urllib.parse
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


# ══════════════════════════════════════════════════
# 数据结构
# ══════════════════════════════════════════════════

@dataclass
class SearchResult:
    """一次搜索返回的单个结果"""
    title: str
    snippet: str
    source: str        # Wikipedia | Baike | GitHub | arXiv | Bilibili | BaiduNews
    url: str
    relevance: float   # 0-1 估计相关性
    content: str = ""  # 延迟加载的网页正文
    fetched: bool = False
    fetch_date: str = ""


@dataclass
class Citation:
    """引用信息"""
    source: str
    title: str
    url: str
    snippet: str
    fetch_date: str
    confidence: float


# ══════════════════════════════════════════════════
# ContentFetcher — 网页内容抓取和正文提取
# ══════════════════════════════════════════════════

class ContentFetcher:
    """
    抓取 URL 并提取正文纯文本。

    使用 urllib + regex 实现，无外部依赖。
    正文提取策略依次尝试：meta description → <p> 段落 → <title>
    """

    REQUEST_HEADERS = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def fetch_and_extract(self, url: str) -> Optional[str]:
        """完整流程：抓取 → 提取正文 → 清洗"""
        html = self._fetch_raw(url)
        if not html:
            return None
        text = self._extract_text(html)
        return self._clean_text(text)

    def _fetch_raw(self, url: str) -> Optional[str]:
        """HTTP GET 请求，返回 HTML 字符串"""
        try:
            req = urllib.request.Request(url, headers=self.REQUEST_HEADERS)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
                # 尝试从 Content-Type 或 HTML 检测编码
                charset = self._detect_charset(resp.headers.get("Content-Type", ""), raw)
                return raw.decode(charset, errors="replace")
        except Exception:
            return None

    def _detect_charset(self, content_type: str, raw: bytes) -> str:
        """检测编码：先看 Content-Type，再看 HTML meta，默认 utf-8"""
        # Content-Type header
        m = re.search(r'charset=([\w-]+)', content_type, re.I)
        if m:
            return m.group(1)
        # HTML meta charset
        m = re.search(rb'<meta[^>]+charset=["\']?([\w-]+)', raw, re.I)
        if m:
            return m.group(1).decode("ascii", errors="ignore")
        # HTML meta http-equiv
        m = re.search(rb'charset=([\w-]+)', raw, re.I)
        if m:
            return m.group(1).decode("ascii", errors="ignore")
        return "utf-8"

    def _extract_text(self, html: str) -> str:
        """从 HTML 提取正文文本"""
        if not html:
            return ""

        # 移除 script 和 style
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.I | re.S)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.I | re.S)
        html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.I | re.S)

        # 尝试提取 meta description
        meta = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if meta:
            return meta.group(1)

        # 提取 <p> 标签内容
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.I | re.S)
        if paragraphs:
            texts = [re.sub(r'<[^>]+>', '', p) for p in paragraphs]
            texts = [re.sub(r'\s+', ' ', t).strip() for t in texts if t.strip()]
            if texts:
                return "\n\n".join(texts)

        # fallback: 提取 <div> 内容
        divs = re.findall(r'<div[^>]*>(.*?)</div>', html, re.I | re.S)
        if divs:
            texts = [re.sub(r'<[^>]+>', '', d) for d in divs]
            texts = [re.sub(r'\s+', ' ', t).strip() for t in texts if len(t.strip()) > 50]
            if texts:
                return "\n\n".join(texts[:5])

        # 最后的 fallback：去掉所有标签
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:2000] if text else ""

    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """清洗和截断文本"""
        if not text:
            return None
        text = re.sub(r'\s+', ' ', text).strip()
        # 移除空行重复
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 截断到 5000 字符
        if len(text) > 5000:
            text = text[:5000] + "\n...(截断)"
        return text if len(text) > 20 else None  # 太短无意义


# ══════════════════════════════════════════════════
# MultiSourceSearcher — 同时搜索多个来源
# ══════════════════════════════════════════════════

class MultiSourceSearcher:
    """
    给定一个查询，同时搜索所有可用来源。

    所有搜索方法独立 try/except，任一来源失败不影响其他。
    """

    # 来源置信度权重
    SOURCE_CONFIDENCE = {
        "Wikipedia": 0.9,
        "arXiv": 0.9,
        "StackOverflow": 0.8,
        "GitHub": 0.7,
        "BaiduNews": 0.6,
        "Bilibili": 0.5,
    }

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.fetcher = ContentFetcher(timeout=timeout)

    def search_all(self, query: str) -> List[SearchResult]:
        """
        搜索所有来源，去重后排好序返回。
        空查询直接返回 []。
        """
        if not query or not query.strip():
            return []

        print(f"  🔎 搜索: \"{query}\" (6 源)")
        all_results = []

        # 并行调每个源（实际上顺序执行，但每个独立 try/except）
        searchers = [
            ("Wikipedia", self._search_wikipedia),
            ("StackOverflow", self._search_stackoverflow),
            ("GitHub", self._search_github),
            ("arXiv", self._search_arxiv),
            ("Bilibili", self._search_bilibili),
            ("BaiduNews", self._search_baidu_news),
        ]

        for name, searcher in searchers:
            try:
                results = searcher(query)
                if results:
                    print(f"    {name}: {len(results)} 条")
                    all_results.extend(results)
                else:
                    print(f"    {name}: 无结果")
            except Exception as e:
                print(f"    {name}: 出错 ({e})")
            time.sleep(0.3)  # 源之间间隔

        # 去重
        deduped = self._deduplicate(all_results)
        # 按相关性排序
        deduped.sort(key=lambda r: r.relevance * self.SOURCE_CONFIDENCE.get(r.source, 0.5), reverse=True)

        print(f"  📊 合计 {len(deduped)} 条 (去重后)")
        return deduped

    # ── 各来源搜索方法 ──

    def _search_wikipedia(self, query: str) -> List[SearchResult]:
        """Wikipedia 搜索 — opensearch（前缀匹配）+ search API（全文搜索）双通道"""
        results = []
        seen_titles = set()
        query_words = set(w.lower() for w in query.split() if len(w) > 2)
        min_title_match = 2 if len(query_words) >= 3 else 1

        # ── 通道1: opensearch（精确前缀匹配，快速） ──
        candidates = self._wiki_query_candidates(query)
        candidates = sorted(set(candidates), key=lambda c: -len(c))

        for candidate in candidates:
            if len(results) >= 3:
                break
            params = urllib.parse.urlencode({
                "action": "opensearch",
                "search": candidate,
                "limit": 2,
                "format": "json",
                "namespace": 0,
            })
            url = f"https://en.wikipedia.org/w/api.php?{params}"
            data = self._fetch_json(url)
            if not data or len(data) < 4:
                continue

            titles, descriptions, links = data[1], data[2], data[3]
            for i in range(len(titles)):
                title = titles[i]
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                # 过滤：opensearch 前缀匹配经常误报，要求标题含至少 min_title_match 个查询词
                title_lower = title.lower()
                match_count = sum(1 for w in query_words if w in title_lower)
                if match_count < min_title_match:
                    continue
                snippet = descriptions[i] if i < len(descriptions) else ""
                link = links[i] if i < len(links) else ""
                self._append_wiki_result(results, title, snippet, link)
                if len(results) >= 5:
                    break

        # ── 通道2: 全文搜索 API（搜索 API 自带相关性排序，不做额外过滤） ──
        if len(results) < 3:
            sr_params = urllib.parse.urlencode({
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": 8,
                "format": "json",
            })
            sr_url = f"https://en.wikipedia.org/w/api.php?{sr_params}"
            sr_data = self._fetch_json(sr_url)
            if sr_data:
                pages = sr_data.get("query", {}).get("search", [])
                for page in pages:
                    title = page.get("title", "")
                    if title in seen_titles:
                        continue
                    seen_titles.add(title)
                    snippet = page.get("snippet", "")
                    import re
                    snippet = re.sub(r"<[^>]+>", "", snippet)
                    page_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                    self._append_wiki_result(results, title, snippet, page_url)
                    if len(results) >= 5:
                        break

        return results

    def _append_wiki_result(self, results, title, snippet, url):
        """辅助：构造 Wikipedia 结果并添加到列表"""
        content = ""
        fetched = False
        if len(results) < 3:
            content = self.fetcher.fetch_and_extract(url) if url else ""
            fetched = bool(content)
        results.append(SearchResult(
            title=title, snippet=snippet[:200],
            source="Wikipedia", url=url,
            relevance=0.85,
            content=content or "", fetched=fetched,
            fetch_date=datetime.now().isoformat()[:10],
        ))

    def _wiki_query_candidates(self, query: str) -> List[str]:
        """生成 Wikipedia 查询候选项 — 所有连续子串，从长到短"""
        candidates = []
        words = query.split()
        n = len(words)

        # 生成所有连续子串，按长度降序
        for length in range(n, 1, -1):  # ≥2 词，跳过单词
            level = []
            for start in range(n - length + 1):
                sub = " ".join(words[start:start + length])
                if sub not in level:
                    level.append(sub)
            # 同长度时，靠后开始的优先（去掉前导限定词）
            level.reverse()
            for c in level:
                if c not in candidates:
                    candidates.append(c)

        # 只有短查询才尝试单次回退
        if n <= 2:
            for w in reversed(words):
                if w not in candidates:
                    candidates.append(w)

        candidates = candidates[:8]  # 最多 8 个候选
        return candidates

    def _search_stackoverflow(self, query: str) -> List[SearchResult]:
        """Stack Overflow API — 按标题关键词搜索"""
        # 去掉常见的修饰词，保留核心关键词
        skip = {"definition", "examples", "applications", "principles",
                "tutorial", "guide", "overview", "introduction", "basics",
                "fundamentals", "reference", "cheatsheet", "concepts"}
        words = [w for w in query.split() if w.lower() not in skip]
        if not words:
            words = query.split()
        core_query = " ".join(words[:4])  # 最多4个词
        params = urllib.parse.urlencode({
            "order": "desc", "sort": "relevance",
            "intitle": core_query, "site": "stackoverflow",
            "pagesize": 5, "filter": "withbody",
        })
        url = f"https://api.stackexchange.com/2.3/search?{params}"
        headers = {"User-Agent": "Week8Bot/1.0"}
        data = self._fetch_json(url, headers)
        if not data or "items" not in data:
            return []

        results = []
        for item in data["items"][:5]:
            title = item.get("title", "")
            body = item.get("body", "")
            snippet = re.sub(r'<[^>]+>', '', body)[:300] if body else ""
            results.append(SearchResult(
                title=title, snippet=snippet,
                source="StackOverflow",
                url=item.get("link", ""),
                relevance=min(0.9, 0.5 + item.get("score", 0) * 0.01),
                content=snippet, fetched=False,
                fetch_date=datetime.now().isoformat()[:10],
            ))
        return results

    def _search_github(self, query: str) -> List[SearchResult]:
        """GitHub 搜索 API"""
        params = urllib.parse.urlencode({
            "q": query, "sort": "stars", "per_page": 5,
        })
        url = f"https://api.github.com/search/repositories?{params}"
        data = self._fetch_json(url, headers={"Accept": "application/vnd.github.v3+json"})
        if not data or "items" not in data:
            return []
        results = []
        for item in data["items"][:5]:
            results.append(SearchResult(
                title=item.get("full_name", ""),
                snippet=(item.get("description") or "")[:200],
                source="GitHub", url=item.get("html_url", ""),
                relevance=min(0.9, item.get("stargazers_count", 0) / 10000 + 0.3),
                fetch_date=datetime.now().isoformat()[:10],
            ))
        return results

    def _search_arxiv(self, query: str) -> List[SearchResult]:
        """arXiv API 搜索"""
        params = urllib.parse.urlencode({
            "search_query": f"all:{query}", "start": 0, "max_results": 5,
        })
        url = f"http://export.arxiv.org/api/query?{params}"
        xml = self._fetch_raw(url)
        if not xml:
            return []
        results = []
        entries = re.findall(r'<entry>(.*?)</entry>', xml, re.I | re.S)
        for entry in entries[:5]:
            title = re.search(r'<title>(.*?)</title>', entry, re.I | re.S)
            summary = re.search(r'<summary>(.*?)</summary>', entry, re.I | re.S)
            link = re.search(r'<id>(.*?)</id>', entry, re.I | re.S)
            if title:
                results.append(SearchResult(
                    title=title.group(1).strip(),
                    snippet=(summary.group(1).strip()[:200] if summary else ""),
                    source="arXiv", url=link.group(1).strip() if link else "",
                    relevance=0.8,
                    fetch_date=datetime.now().isoformat()[:10],
                ))
        return results

    def _search_bilibili(self, query: str) -> List[SearchResult]:
        """Bilibili 搜索"""
        params = urllib.parse.urlencode({"keyword": query, "search_type": "video", "page": 1})
        url = f"https://api.bilibili.com/x/web-interface/search/all/v2?{params}"
        data = self._fetch_json(url, headers={
            "Referer": "https://search.bilibili.com",
            "User-Agent": self.fetcher.REQUEST_HEADERS["User-Agent"],
        })
        if not data or data.get("code") != 0:
            return []
        results = []
        # B 站 API 结果结构较深
        try:
            for module in data.get("data", {}).get("result", []):
                for item in module.get("data", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        snippet=item.get("desc", "")[:200],
                        source="Bilibili",
                        url=f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                        relevance=0.5,
                        fetch_date=datetime.now().isoformat()[:10],
                    ))
        except Exception:
            pass
        return results[:5]

    def _search_baidu_news(self, query: str) -> List[SearchResult]:
        """百度新闻搜索"""
        params = urllib.parse.urlencode({"word": query, "tn": "news", "from": "news"})
        url = f"https://news.baidu.com/s?{params}"
        html = self._fetch_raw(url)
        if not html:
            return []
        results = []
        # 提取新闻标题和链接
        items = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.I)
        seen = set()
        for link, title in items:
            title_clean = re.sub(r'<[^>]+>', '', title).strip()
            if not title_clean or len(title_clean) < 5:
                continue
            if title_clean in seen:
                continue
            seen.add(title_clean)
            results.append(SearchResult(
                title=title_clean, snippet="",
                source="BaiduNews", url=link,
                relevance=0.5,
                fetch_date=datetime.now().isoformat()[:10],
            ))
            if len(results) >= 5:
                break
        return results

    # ── 工具 ──

    def _fetch_json(self, url: str, headers: Dict = None) -> Optional[Dict]:
        """GET JSON 响应"""
        all_headers = dict(self.fetcher.REQUEST_HEADERS)
        if headers:
            all_headers.update(headers)
        try:
            req = urllib.request.Request(url, headers=all_headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8", errors="replace"))
        except Exception:
            return None

    def _fetch_raw(self, url: str) -> Optional[str]:
        """GET 原始响应"""
        try:
            req = urllib.request.Request(url, headers=self.fetcher.REQUEST_HEADERS)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
                charset = self.fetcher._detect_charset(resp.headers.get("Content-Type", ""), raw)
                return raw.decode(charset, errors="replace")
        except Exception:
            return None

    def _deduplicate(self, results: List[SearchResult]) -> List[SearchResult]:
        """按 URL 和标题去重"""
        seen_urls = set()
        seen_titles = set()
        deduped = []
        for r in results:
            # URL 去重
            url_key = r.url[:80]
            if url_key in seen_urls:
                continue
            # 标题前 20 字去重
            title_key = r.title[:20].lower()
            if title_key in seen_titles:
                continue
            seen_urls.add(url_key)
            seen_titles.add(title_key)
            deduped.append(r)
        return deduped


# ══════════════════════════════════════════════════
# AnswerSynthesizer — 多源答案综合
# ══════════════════════════════════════════════════

class AnswerSynthesizer:
    """
    把多个来源的搜索结果综合为一个结构化答案。

    包含引用信息，支持存入 KnowledgeBase。
    """

    def synthesize(self, query: str, results: List[SearchResult]) -> Dict[str, Any]:
        """
        综合搜索结果，返回结构化答案 dict。

        自动抓取 top 结果的内容（若尚未抓取）。
        """
        if not results:
            return {
                "topic": f"研究: {query}",
                "summary": f"搜索 \"{query}\" 未找到有效结果",
                "key_points": [],
                "citations": [],
                "sources_used": [],
                "all_results_count": 0,
            }

        # 取 top 5
        ranked = sorted(results, key=lambda r: r.relevance * MultiSourceSearcher.SOURCE_CONFIDENCE.get(r.source, 0.5), reverse=True)
        top = ranked[:5]

        # 对还没有抓取内容的 top 结果补充抓取
        fetcher = ContentFetcher()
        for r in top:
            if not r.fetched and r.url:
                try:
                    content = fetcher.fetch_and_extract(r.url)
                    if content:
                        r.content = content
                        r.fetched = True
                except Exception:
                    pass

        citations = self._build_citations(top)
        sources_used = list(set(c.source for c in citations))

        # 生成摘要 — 优先用已抓取正文，按来源分组
        source_groups = {}
        for r in top:
            sg = source_groups.setdefault(r.source, [])
            text = r.content.strip() if r.content else r.snippet.strip() if r.snippet else ""
            if text:
                sg.append((r.title, text[:300]))

        summary_parts = [f"关于「{query}」的多源研究结果。"]
        for source, items in source_groups.items():
            summary_parts.append(f"\n📖 {source}:")
            for title, text in items[:2]:
                summary_parts.append(f"  • {title}: {text[:200].strip()}")

        summary = "\n".join(summary_parts)
        summary += f"\n\n共检索 {len(results)} 条，覆盖 {len(sources_used)} 个来源。"

        # 关键发现 — 从已抓取正文提取有意义的句子
        key_points = []
        for r in top[:5]:
            text = r.content or r.snippet or ""
            text = text.strip()
            if not text:
                continue
            # 从正文中提取看起来像核心观点的短句
            sentences = [s.strip() for s in text.replace("\n", "。").split("。") if len(s.strip()) > 15]
            if sentences:
                best = max(sentences[:5], key=len)[:150]
                key_points.append(f"[{r.source}] {r.title}: {best}")
            else:
                key_points.append(f"[{r.source}] {r.title}: {text[:150]}")

        return {
            "topic": f"研究: {query}",
            "summary": summary,
            "key_points": key_points[:5],
            "citations": citations,
            "sources_used": sources_used,
            "all_results_count": len(results),
            "top_results": [{
                "title": r.title, "source": r.source,
                "url": r.url, "snippet": (r.content or r.snippet or "")[:200],
            } for r in top],
            "query": query,
            "research_date": datetime.now().isoformat(),
        }

    def _build_citations(self, results: List[SearchResult]) -> List[Citation]:
        """从搜索结果构建引用"""
        return [
            Citation(
                source=r.source, title=r.title, url=r.url,
                snippet=(r.content or r.snippet or "")[:150],
                fetch_date=r.fetch_date,
                confidence=MultiSourceSearcher.SOURCE_CONFIDENCE.get(r.source, 0.5),
            ) for r in results
        ]

    def make_kb_entry(self, query: str, answer: Dict) -> Dict[str, Any]:
        """构建 KB 兼容的知识条目"""
        citations = answer.get("citations", [])
        refs = [{"source": c["source"] if isinstance(c, dict) else c.source,
                 "url": c["url"] if isinstance(c, dict) else c.url,
                 "snippet": c["snippet"] if isinstance(c, dict) else c.snippet}
                for c in citations]
        return {
            "topic": answer.get("topic", f"研究: {query}"),
            "category": "网络研究",
            "content": answer.get("summary", ""),
            "source": "web_researcher",
            "keywords": [query, "web_research"] + answer.get("sources_used", []),
            "references": refs[:5],
            "citations": refs[:5],
            "sources_used": answer.get("sources_used", []),
            "all_results_count": answer.get("all_results_count", 0),
            "importance": 0.85,
            "learning_depth": 2,
        }


# ══════════════════════════════════════════════════
# 主入口 — 单测
# ══════════════════════════════════════════════════

def test_content_fetcher():
    """单元测试：正文提取"""
    fetcher = ContentFetcher()

    # 空 HTML
    assert fetcher._extract_text("") == ""

    # 只含 script
    empty = fetcher._extract_text("<script>alert('x')</script>")
    assert "alert" not in empty, f"script 内容未被移除: {empty[:50]}"

    # 正常段落
    html = "<html><body><p>第一段内容</p><p>第二段内容</p></body></html>"
    text = fetcher._extract_text(html)
    assert "第一段" in text, f"段落提取失败: {text}"
    assert "第二段" in text

    # 截断
    long = "x" * 6000
    cut = fetcher._clean_text(long)
    assert cut is not None and len(cut) <= 5100, f"截断失败: {len(cut) if cut else 0}"

    # 太短被过滤
    short = fetcher._clean_text("a")
    assert short is None, "短文本应返回 None"

    print("  [OK] ContentFetcher 所有测试通过")


def test_search_mocks():
    """模拟测试去重和排序"""
    searcher = MultiSourceSearcher()
    results = [
        SearchResult("A", "desc", "GitHub", "http://a.com", 0.8),
        SearchResult("A", "desc2", "Wikipedia", "http://a.com", 0.9),  # 同 URL
        SearchResult("B", "desc", "arXiv", "http://b.com", 0.7),
        SearchResult("C", "desc", "Baike", "http://c.com", 0.6),
    ]
    deduped = searcher._deduplicate(results)
    assert len(deduped) == 3, f"去重后应为 3，实际 {len(deduped)}"
    assert deduped[0].source == "GitHub", "去重保留首个出现（GitHub 先于 Wikipedia）"

    # 空输入
    assert searcher.search_all("") == []

    # 空结果去重
    assert searcher._deduplicate([]) == []

    print("  [OK] MultiSourceSearcher 模拟测试通过")


def test_answer_synthesizer():
    """测试答案综合"""
    syn = AnswerSynthesizer()
    results = [
        SearchResult("Test Topic", "A useful snippet", "Wikipedia",
                     "http://wiki.com", 0.9, content="Full content here"),
        SearchResult("GitHub Repo", "A repo about it", "GitHub",
                     "http://github.com", 0.7),
    ]
    answer = syn.synthesize("test query", results)
    assert answer["all_results_count"] == 2
    assert len(answer["citations"]) == 2
    assert len(answer["key_points"]) == 2
    assert "test query" in answer["summary"]

    # 空结果
    empty = syn.synthesize("empty", [])
    assert empty["all_results_count"] == 0
    assert "未找到" in empty["summary"]

    # KB entry
    entry = syn.make_kb_entry("test", answer)
    assert entry["category"] == "网络研究"
    assert entry["importance"] == 0.85
    assert len(entry["references"]) == 2

    print("  [OK] AnswerSynthesizer 所有测试通过")


if __name__ == "__main__":
    print("=" * 50)
    print("  Web Researcher 测试")
    print("=" * 50)

    test_content_fetcher()
    test_search_mocks()
    test_answer_synthesizer()

    # 真实搜索测试（依赖网络）
    print("\n  🌐 真实搜索测试:")
    searcher = MultiSourceSearcher()
    results = searcher.search_all("Python programming language")
    print(f"  总结果: {len(results)} 条")
    for r in results[:3]:
        print(f"    [{r.relevance:.1f}][{r.source}] {r.title[:60]}")
        if r.content:
            print(f"      正文: {r.content[:100]}...")

    syn = AnswerSynthesizer()
    answer = syn.synthesize("Python", results)
    print(f"\n  综合摘要: {answer['summary'][:150]}...")
    print(f"  引用数: {len(answer['citations'])}")
    print(f"  来源: {answer['sources_used']}")

    print("\n✅ Web Researcher 全部测试完成")
