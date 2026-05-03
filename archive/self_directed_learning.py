#!/usr/bin/env python3
"""
🧠 星期八自主学习系统
分析知识缺口 → 定向爬取 → 学习消化
"""

import os, sys, json, time, urllib.request, ssl
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# ─── 知识领域图谱 ──────────────────────────────────────────
# 我应当掌握的领域及子话题
KNOWLEDGE_MAP = {
    "编程语言": [
        "Python基础语法", "Python高级特性", "JavaScript ES6+",
        "TypeScript", "Go语言", "Rust语言", "C++现代语法",
        "Shell脚本", "SQL",
    ],
    "前后端开发": [
        "React框架", "Vue框架", "Next.js", "Node.js后端",
        "FastAPI", "Flask", "Django", "RESTful API设计",
        "GraphQL", "WebSocket", "CSS/HTML5",
    ],
    "数据库": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis",
        "SQLite", "Elasticsearch", "数据库设计范式",
        "索引优化", "事务与锁",
    ],
    "DevOps与运维": [
        "Docker容器化", "Kubernetes", "CI/CD流水线",
        "Linux系统管理", "Nginx配置", "Git高级操作",
        "云服务(AWS/阿里云)", "监控与日志",
    ],
    "AI与机器学习": [
        "机器学习算法", "深度学习", "自然语言处理",
        "大语言模型原理", "Prompt Engineering", "RAG技术",
        "模型微调", "AI Agent框架", "计算机视觉",
    ],
    "数据结构与算法": [
        "数组与链表", "树与图", "哈希表", "排序算法",
        "动态规划", "贪心算法", "时间复杂度分析",
        "设计模式",
    ],
    "系统设计": [
        "微服务架构", "消息队列", "分布式系统",
        "缓存策略", "负载均衡", "API网关",
        "系统高可用设计", "CAP理论",
    ],
    "计算机基础": [
        "操作系统原理", "计算机网络", "编译原理",
        "内存管理", "进程与线程", "TCP/IP协议",
        "HTTP/HTTPS协议",
    ],
    "安全": [
        "Web安全", "OWASP Top 10", "认证与授权",
        "数据加密", "安全编码实践",
    ],
    "工具与效率": [
        "VS Code高级用法", "Vim/Neovim", "正则表达式",
        "数据分析Pandas", "数据可视化",
        "自动化测试", "性能优化",
    ],
}


class SelfDirectedLearner:
    """星期八自主学习引擎"""

    def __init__(self):
        self.data_dir = Path("data")
        self.kb = None  # lazy load

    def _load_kb(self):
        if self.kb is None:
            from knowledge_base import KnowledgeBase
            self.kb = KnowledgeBase()

    def get_existing_topics(self) -> Set[str]:
        """获取已学过的所有主题（用于对比缺口）"""
        self._load_kb()
        all_k = self.kb.get_all_knowledge()
        topics = set()
        for k in all_k:
            t = k.get("topic", "")
            topics.add(t[:60])
            # 也从keywords里提取
            for kw in k.get("keywords", []):
                if isinstance(kw, str):
                    topics.add(kw.lower())
        return topics

    def analyze_gaps(self) -> List[Dict]:
        """分析知识缺口，返回需要学习的主题列表"""
        print("🧠 星期八开始自我知识缺口分析...")
        print("=" * 60)

        existing = self.get_existing_topics()
        existing_lower = {e.lower() for e in existing}

        gaps = []
        covered = set()
        total = 0

        for domain, topics in KNOWLEDGE_MAP.items():
            domain_gaps = []
            for topic in topics:
                total += 1
                # 检查是否已有相关知识
                topic_lower = topic.lower()
                found = any(
                    topic_lower in e or e in topic_lower
                    for e in existing_lower
                )
                if found:
                    covered.add(domain)
                else:
                    domain_gaps.append(topic)

            if domain_gaps:
                gaps.append({
                    "domain": domain,
                    "missing": domain_gaps,
                    "count": len(domain_gaps),
                    "search_queries": [
                        f"{topic} 教程" if "基础" in topic or "入门" in topic
                        else topic
                        for topic in domain_gaps[:3]  # 每个领域最多3个搜索词
                    ],
                })

        # 打印分析报告
        print(f"\n📊 知识领域总览:")
        for domain, topics in KNOWLEDGE_MAP.items():
            has = domain in covered
            icon = "✅" if has else "❌"
            print(f"   {icon} {domain}: {len(topics)}个子话题")

        print(f"\n📋 详细缺口分析:")
        total_gaps = sum(g["count"] for g in gaps)
        print(f"   已覆盖领域: {len(covered)}/{len(KNOWLEDGE_MAP)}")
        print(f"   缺口主题数: {total_gaps}/{total}")
        print()

        for g in gaps:
            print(f"   🔴 {g['domain']} (缺{g['count']}个):")
            for t in g["missing"]:
                print(f"      - {t}")

        print(f"\n🎯 需要执行 {len(gaps)} 个领域的定向爬取")
        return gaps

    def queue_crawler_tasks(self, gaps: List[Dict]):
        """根据缺口列表，告诉爬虫抓什么"""
        print("\n📡 向爬虫下达定向抓取指令...")
        print("=" * 60)

        all_queries = []
        for g in gaps:
            for q in g["search_queries"]:
                all_queries.append({
                    "query": q,
                    "domain": g["domain"],
                    "reason": f"缺少{g['domain']}领域知识",
                })

        # 保存抓取任务队列
        task_file = self.data_dir / "crawler_tasks.json"
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(all_queries, f, ensure_ascii=False, indent=2)

        print(f"   ✅ 已生成 {len(all_queries)} 个定向抓取任务:")
        for task in all_queries:
            print(f"      🎯 [{task['domain']}] {task['query']}")

        return all_queries

    def run_full_cycle(self):
        """完整自主学习循环（只分析缺口+生成任务，爬虫异步执行）"""
        print(f"\n{'='*60}")
        print("🧠 星期八自主学习循环启动")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print('='*60)

        # 1. 分析缺口
        gaps = self.analyze_gaps()

        if not gaps:
            print("\n🎉 所有领域已覆盖！暂时不需要学习新内容。")
            return

        # 2. 生成抓取任务（爬虫下次运行时自动读取执行）
        tasks = self.queue_crawler_tasks(gaps)

        print(f"\n📋 任务队列已保存到 data/crawler_tasks.json")
        print(f"   🎯 共 {len(tasks)} 个定向抓取任务")
        print(f"   ⏰ 爬虫将在下次运行时自动消化这些任务")
        print(f"\n{'='*60}")
        print("✅ 分析完成，爬虫会异步补全知识")
        print(f"{'='*60}")

        return gaps, tasks


def main():
    import urllib.request, ssl
    learner = SelfDirectedLearner()
    learner.run_full_cycle()


if __name__ == "__main__":
    main()
