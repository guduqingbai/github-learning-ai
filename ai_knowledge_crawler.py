#!/usr/bin/env python3
"""
🤖 AI知识自动爬虫 - 真实数据版
使用免费公开API获取全球AI相关资料
"""

import os, sys, time, json, re, urllib.request, urllib.parse, ssl
import threading, schedule
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 跳过SSL验证（某些环境需要）
ctx = ssl._create_unverified_context()


class AIKnowledgeCrawler:
    """AI知识自动爬虫 - 真实数据版"""

    def __init__(self):
        self.is_running = False
        self.crawl_thread = None
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.session_count = 0
        self.last_results = []
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; LearningBot/1.0)"}
        self._log_buffer = []  # 日志缓冲，减少文件I/O

    def log(self, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        self._log_buffer.append(line + "\n")
        if len(self._log_buffer) >= 10:
            self._flush_log()

    def _flush_log(self):
        if not self._log_buffer:
            return
        log_file = self.data_dir / "ai_knowledge_crawler.log"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.writelines(self._log_buffer)
        finally:
            self._log_buffer.clear()

    # ─── 1. GitHub Trending ─────────────────────────────────────
    def crawl_github(self) -> List[Dict]:
        """从GitHub API获取热门AI仓库 + 自思考架构相关项目"""
        results = []
        queries = [
            "machine+learning",
            "deep+learning",
            "natural+language+processing",
            "artificial+intelligence",
            "large+language+model",
            "self+thinking+AI",
            "autonomous+agent+architecture",
            "meta+cognition+AI",
            "curiosity+driven+learning",
            "self+improving+systems",
        ]
        for q in queries:
            try:
                url = f"https://api.github.com/search/repositories?q={q}&sort=stars&per_page=3"
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                    data = json.loads(resp.read().decode())
                    for repo in data.get("items", [])[:3]:
                        results.append({
                            "title": repo["full_name"],
                            "content": repo.get("description", "") or "暂无描述",
                            "source": "GitHub",
                            "importance": min(1.0, repo.get("stargazers_count", 0) / 10000),
                            "link": repo["html_url"],
                            "keywords": [q.replace("+", " ")],
                        })
                time.sleep(1)  # 避免API限流
            except Exception as e:
                self.log(f"⚠️ GitHub搜索失败 [{q}]: {e}")
        return results

    # ─── 2. arXiv论文 ──────────────────────────────────────────
    def crawl_arxiv(self) -> List[Dict]:
        """从arXiv API获取最新AI论文"""
        results = []
        queries = ["AI", "machine+learning", "natural+language+processing"]
        for q in queries:
            try:
                url = f"http://export.arxiv.org/api/query?search_query=all:{q}&sortBy=submittedDate&sortOrder=descending&max_results=3"
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
                    xml = resp.read().decode("utf-8")
                    # 简单解析XML提取标题
                    titles = re.findall(r"<title>(.*?)</title>", xml, re.DOTALL)
                    ids = re.findall(r"<id>(.*?)</id>", xml)
                    summaries = re.findall(r"<summary>(.*?)</summary>", xml, re.DOTALL)
                    for i in range(min(len(titles), 5)):
                        if i == 0:
                            continue  # 跳过feed标题
                        title = titles[i].strip().replace("\n", " ")[:200]
                        summary = (summaries[i-1].strip().replace("\n", " ")[:300]
                                   if i-1 < len(summaries) else "")
                        link = ids[i].strip() if i < len(ids) else url
                        results.append({
                            "title": f"[论文] {title}",
                            "content": summary,
                            "source": "arXiv",
                            "importance": 0.85,
                            "link": link,
                            "keywords": [q.replace("+", " ")],
                        })
                time.sleep(3)  # arXiv要求至少3秒间隔
            except Exception as e:
                self.log(f"⚠️ arXiv搜索失败 [{q}]: {e}")
        return results

    # ─── 3. Hacker News ────────────────────────────────────────
    def crawl_hackernews(self) -> List[Dict]:
        """Hacker News — 被墙快速跳过"""
        body = self._try_source("https://hacker-news.firebaseio.com/v0/topstories.json", 3)
        if not body:
            return []
        results = []
        try:
            story_ids = json.loads(body)[:6]
            for sid in story_ids:
                item = json.loads(self._try_source(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", 3) or "{}")
                if item.get("title"):
                    results.append({
                        "title": item["title"],
                        "content": (item.get("text") or item.get("url") or "HN")[:300],
                        "source": "Hacker News", "importance": 0.7,
                        "link": item.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "keywords": ["tech"],
                    })
            self.log(f"✅ Hacker News: {len(results)} 条")
        except Exception:
            pass
        return results

    # ─── 4. 已知被墙源快速探测 ────────────────────────────
    def _try_source(self, url: str, timeout: int = 2) -> str:
        """快速探测源是否可访问，1秒内没回应就放弃"""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return resp.read().decode(errors="replace")
        except Exception:
            return ""

    def crawl_wikipedia(self) -> List[Dict]:
        """Wikipedia — 被墙快速跳过"""
        test = self._try_source("https://en.wikipedia.org/api/rest_v1/page/summary/Artificial_intelligence", 2)
        if not test:
            return []
        topics = ["Artificial_intelligence", "Machine_learning", "Deep_learning", "Natural_language_processing"]
        results = []
        for topic in topics:
            try:
                data = json.loads(self._try_source(
                    f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}", 3) or "{}")
                if not data.get("title"):
                    continue
                results.append({
                    "title": data["title"], "content": (data.get("extract") or "")[:400],
                    "source": "Wikipedia", "importance": 0.8,
                    "link": data.get("content_urls", {}).get("desktop", {}).get("page",
                           f"https://en.wikipedia.org/wiki/{topic}"),
                    "keywords": [topic.replace("_", " ")],
                })
            except Exception:
                continue
        if results:
            self.log(f"✅ Wikipedia: {len(results)} 条")
        return results

    # ─── 5. Reddit (双协议) ────────────────────────────────────
    def crawl_reddit(self) -> List[Dict]:
        """Reddit — 被墙快速跳过"""
        body = self._try_source("https://www.reddit.com/r/artificial/hot.json?limit=5", 2)
        if not body:
            return []
        try:
            data = json.loads(body)
            results = []
            for p in data.get("data", {}).get("children", [])[:5]:
                d = p.get("data", {})
                results.append({
                    "title": d.get("title", ""),
                    "content": (d.get("selftext") or "")[:200] or "Reddit讨论",
                    "source": "Reddit", "importance": 0.7,
                    "link": f"https://reddit.com{d.get('permalink', '')}",
                    "keywords": ["reddit"],
                })
            return results
        except Exception:
            return []

    # ─── 6. 百度百科 (国内版 Wikipedia) ──────────────────────────
    def crawl_baike(self) -> List[Dict]:
        """百度百科AI词条 — 国内可正常访问"""
        results = []
        topics = {
            "人工智能": "https://baike.baidu.com/item/%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD",
            "机器学习": "https://baike.baidu.com/item/%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0",
            "深度学习": "https://baike.baidu.com/item/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0",
            "自然语言处理": "https://baike.baidu.com/item/%E8%87%AA%E7%84%B6%E8%AF%AD%E8%A8%80%E5%A4%84%E7%90%86",
            "大语言模型": "https://baike.baidu.com/item/%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B",
        }
        for name, url in topics.items():
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                    html = resp.read().decode("utf-8", errors="replace")
                    # 提取摘要
                    desc_match = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', html)
                    desc = desc_match.group(1)[:400] if desc_match else f"百度百科词条: {name}"
                    # 提取标题
                    title_match = re.search(r'<title>([^<]+)</title>', html)
                    title = title_match.group(1).replace("_百度百科", "") if title_match else name
                    results.append({
                        "title": title.strip(),
                        "content": desc,
                        "source": "百度百科",
                        "importance": 0.8,
                        "link": url,
                        "keywords": [name],
                    })
                self.log(f"✅ 百度百科: [{name}] 获取成功")
                time.sleep(0.5)
            except Exception as e:
                self.log(f"⚠️ 百度百科抓取失败 [{name}]: {e}")
        return results

    # ─── 7. 哔哩哔哩 (搜索科技区) ──────────────────────────
    def crawl_bilibili(self) -> List[Dict]:
        """B站搜索AI相关视频"""
        results = []
        queries = ["人工智能", "机器学习", "Python编程"]
        browser_hdrs = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://search.bilibili.com/",
            "Origin": "https://search.bilibili.com",
        }
        ai_keywords = ["AI", "人工智能", "机器学习", "深度学习", "Python",
                       "教程", "算法", "模型", "编程", "数据"]
        for q in queries:
            try:
                url = f"https://search.bilibili.com/all?keyword={urllib.parse.quote(q)}&from_source=webtop_search"
                req = urllib.request.Request(url, headers=browser_hdrs)
                with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                    html = resp.read().decode("utf-8", errors="replace")
                    # 提取所有视频标题（B站服务端渲染的标题在 title 属性中）
                    all_titles = re.findall(r'title="([^"]{4,80})"', html)
                    seen = set()
                    for t in all_titles:
                        t = t.strip()
                        if not t or len(t) < 5 or t in seen:
                            continue
                        seen.add(t)
                        # 只保留与AI/技术相关的标题
                        if any(kw in t for kw in ai_keywords):
                            results.append({
                                "title": f"[B站] {t}",
                                "content": f"B站AI学习视频: {q}",
                                "source": "B站",
                                "importance": 0.7,
                                "link": url,
                                "keywords": [q],
                            })
                self.log(f"✅ B站[{q}]: 获取到 {len(results)} 个视频")
                time.sleep(1)
            except Exception as e:
                self.log(f"⚠️ B站搜索失败 [{q}]: {e}")
        return results

    # ─── 8. 百度新闻热搜 ───────────────────────────────────
    def crawl_baidu_news(self) -> List[Dict]:
        """百度实时热搜中的科技新闻"""
        results = []
        try:
            url = "https://top.baidu.com/board?tab=realtime"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                html = resp.read().decode("utf-8", errors="replace")
                # 提取热搜标题
                items = re.findall(r'"word":"([^"]+)"', html)
                for item in items[:20]:
                    kw = ["AI", "人工", "模型", "智能", "算法", "数据", "学习",
                          "编程", "代码", "科技", "芯片", "手机", "电脑", "软件",
                          "数字", "网络", "GPT", "苹果", "华为", "微软", "谷歌"]
                    if any(k in item for k in kw):
                        results.append({
                            "title": item,
                            "content": "百度实时热搜",
                            "source": "百度热搜",
                            "importance": 0.7,
                            "link": f"https://www.baidu.com/s?wd={urllib.parse.quote(item)}",
                            "keywords": ["科技", "热搜"],
                        })
            self.log(f"✅ 百度热搜: 获取到 {len(results)} 条科技相关热搜")
        except Exception as e:
            self.log(f"⚠️ 百度热搜抓取失败: {e}")
        return results

    # ─── 9. 从任务队列抓取（自主学习生成的定向任务）───────────
    def crawl_task_queue(self) -> List[Dict]:
        """读取星期八的自主学习任务队列，逐任务原子处理"""
        task_file = self.data_dir / "crawler_tasks.json"
        if not task_file.exists():
            return []

        with open(task_file, "r", encoding="utf-8") as f:
            tasks = json.load(f)

        if not tasks:
            return []

        limit = min(5, len(tasks))
        self.log(f"🎯 读取自主学习任务队列: 共{len(tasks)}个, 本次处理{limit}个")

        results = []
        for _ in range(limit):
            # 重新读取最新队列
            with open(task_file, "r", encoding="utf-8") as f:
                current = json.load(f)
            if not current:
                break

            task = current.pop(0)  # 取出第一个任务
            query = task["query"]
            domain = task.get("domain", "知识学习")
            self.log(f"   📌 定向抓取: [{domain}] {query}")

            try:
                quoted = urllib.parse.quote(query)
                body = self._try_source(
                    f"https://api.github.com/search/repositories?q={quoted}&sort=stars&per_page=3",
                    timeout=8)
                if body:
                    data = json.loads(body)
                    for repo in data.get("items", [])[:3]:
                        results.append({
                            "title": f"[{domain}] {repo['full_name']} - {(repo.get('description') or '')[:80]}",
                            "content": (repo.get("description") or f"{query}相关项目")[:400],
                            "source": f"定向爬虫/{domain}",
                            "importance": min(1.0, repo.get("stargazers_count", 0) / 5000 + 0.5),
                            "link": repo["html_url"],
                            "keywords": [domain, query],
                        })
                # 处理成功，将剩余队列写回文件
                if current:
                    with open(task_file, "w", encoding="utf-8") as f:
                        json.dump(current, f, ensure_ascii=False, indent=2)
                else:
                    task_file.unlink()
                    self.log("🎉 所有定向任务已完成！")
                time.sleep(1.5)
            except Exception as e:
                self.log(f"   ⚠️ 定向抓取失败 [{query}]: {e}")
                # 失败的任务放回队列头部，下次重试
                current.insert(0, task)
                with open(task_file, "w", encoding="utf-8") as f:
                    json.dump(current, f, ensure_ascii=False, indent=2)
                break  # 停止后续任务

        if results:
            self.log(f"✅ 定向抓取: 获取 {len(results)} 条知识")
        return results

    # ─── 保存到知识库 ──────────────────────────────────────────
    def save_knowledge(self, items: List[Dict]):
        if not items:
            self.log("📭 没有新知识需要保存")
            return
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            count = 0
            for item in items:
                entry = {
                    "topic": item["title"],
                    "category": "人工智能",
                    "content": item["content"],
                    "source": item["source"],
                    "keywords": item.get("keywords", ["AI"]),
                    "references": [item.get("link", "")],
                    "importance": item.get("importance", 0.5),
                    "learning_time": datetime.now().isoformat(),
                }
                kb.learn_from_experience(entry)
                count += 1
            self.log(f"✅ 保存 {count} 条知识到知识库")
        except Exception as e:
            self.log(f"❌ 保存知识失败: {e}")

    # ─── 执行完整爬取 ──────────────────────────────────────────
    def crawl_all(self):
        """执行一次完整爬取"""
        self.session_count += 1
        self.log(f"🚀 [第{self.session_count}次] 开始爬取全球AI资料")
        print("=" * 60)

        all_items = []

        self.log("🌐 正在爬取 GitHub 热门AI项目...")
        all_items.extend(self.crawl_github())

        self.log("📄 正在爬取 arXiv 最新论文...")
        all_items.extend(self.crawl_arxiv())

        self.log("📰 正在爬取 Hacker News 技术热议...")
        all_items.extend(self.crawl_hackernews())

        self.log("📚 正在爬取 Wikipedia AI条目...")
        all_items.extend(self.crawl_wikipedia())

        self.log("💬 正在爬取 Reddit AI讨论...")
        all_items.extend(self.crawl_reddit())

        # 国内源
        self.log("🇨🇳 正在爬取 百度百科 AI词条...")
        all_items.extend(self.crawl_baike())

        self.log("🇨🇳 正在爬取 B站 AI教学视频...")
        all_items.extend(self.crawl_bilibili())

        self.log("🇨🇳 正在爬取 百度热搜 科技资讯...")
        all_items.extend(self.crawl_baidu_news())

        # 定向任务（自主学习生成的缺口补充）
        self.log("🎯 正在执行自主学习定向任务...")
        all_items.extend(self.crawl_task_queue())

        # 去重
        seen = set()
        unique = []
        for item in all_items:
            key = item["title"][:50]
            if key not in seen:
                seen.add(key)
                unique.append(item)

        self.log(f"\n📊 本次爬取汇总:")
        sources = {}
        for item in unique:
            src = item["source"]
            sources[src] = sources.get(src, 0) + 1
        for src, cnt in sorted(sources.items()):
            self.log(f"   {src}: {cnt} 条")
        self.log(f"  共计: {len(unique)} 条 (去重后)")

        self.save_knowledge(unique)
        self.last_results = unique
        self._flush_log()
        self.log(f"✅ [第{self.session_count}次] 爬取完成\n")

    # ─── 调度器 ────────────────────────────────────────────────
    def run_scheduler(self):
        schedule.every(2).hours.at(":00").do(self.crawl_all)
        self.log("⏰ 调度器已启动，每2小时整点执行爬取")
        self.crawl_all()  # 立即执行一次
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)

    def start(self):
        if self.is_running:
            self.log("⚠️ 爬虫已在运行")
            return
        self.is_running = True
        self.crawl_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.crawl_thread.start()
        self.log("✅ AI知识爬虫启动成功 (真实数据版)")

    def stop(self):
        self.log("🛑 正在停止爬虫...")
        self.is_running = False
        if self.crawl_thread:
            self.crawl_thread.join(timeout=10)
        self.log("✅ 爬虫已停止")

    def get_status(self) -> Dict:
        log_file = self.data_dir / "ai_knowledge_crawler.log"
        recent = []
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()[-15:]
                recent = [l.strip() for l in lines if l.strip()]
        return {
            "running": self.is_running,
            "sessions": self.session_count,
            "sources": ["GitHub", "arXiv", "Hacker News", "Wikipedia", "Reddit", "百度百科", "B站", "百度热搜"],
            "recent_logs": recent,
        }


def main():
    print("🤖 AI知识自动爬虫 (真实数据版)")
    print("=" * 60)
    print("数据源: GitHub Trending | arXiv论文 | Hacker News | Wikipedia | Reddit | 百度百科 | B站 | 百度热搜")
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
