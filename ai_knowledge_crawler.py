#!/usr/bin/env python3
"""
🤖 AI知识自动爬虫 - 定时任务agent
每天每个小时整点自动搜索AI相关知识资料
"""

import os
import sys
import time
import schedule
import threading
import datetime
import random
from typing import List, Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AIKnowledgeCrawler:
    """AI知识自动爬虫类"""

    def __init__(self):
        self.is_running = False
        self.crawl_thread = None
        self.knowledge_sources = [
            "github_trending",
            "arxiv_papers",
            "tech_blogs",
            "research_papers",
            "ai_news"
        ]

        print("🤖 AI知识自动爬虫初始化完成")
        print("🎯 目标：每天每个小时整点自动搜索AI相关知识")
        print("📚 搜索源：GitHub Trending、arXiv论文、技术博客、研究论文、AI新闻")

    def log_message(self, message: str):
        """记录日志消息"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)

        # 保存到日志文件
        log_file = os.path.join("data", "ai_knowledge_crawler.log")
        os.makedirs("data", exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

    def search_github_trending(self) -> List[str]:
        """搜索GitHub热门AI项目"""
        self.log_message("🔍 搜索GitHub热门AI项目...")

        # 模拟搜索结果（实际项目中会使用API）
        github_projects = [
            "LLM微调框架：支持多种大语言模型的快速微调",
            "向量数据库：高性能的AI知识存储解决方案",
            "AI辅助编程：代码生成和修复工具",
            "计算机视觉库：图像处理和分析工具",
            "自然语言处理：文本分析和生成工具"
        ]

        return random.sample(github_projects, 3)

    def search_arxiv_papers(self) -> List[str]:
        """搜索arXiv最新AI论文"""
        self.log_message("🔍 搜索arXiv最新AI论文...")

        # 模拟搜索结果
        arxiv_papers = [
            "大语言模型上下文窗口扩展技术研究",
            "高效注意力机制在AI中的应用",
            "多模态AI融合方法",
            "AI模型压缩和加速技术",
            "联邦学习安全协议"
        ]

        return random.sample(arxiv_papers, 2)

    def search_tech_blogs(self) -> List[str]:
        """搜索技术博客AI文章"""
        self.log_message("🔍 搜索技术博客AI文章...")

        # 模拟搜索结果
        tech_articles = [
            "深度解析Transformer架构演进",
            "AI在医疗领域的应用案例",
            "如何优化AI模型的推理速度",
            "AI训练数据的质量控制",
            "AI部署的最佳实践"
        ]

        return random.sample(tech_articles, 2)

    def search_research_papers(self) -> List[str]:
        """搜索研究机构AI论文"""
        self.log_message("🔍 搜索研究机构AI论文...")

        # 模拟搜索结果
        research_papers = [
            "谷歌DeepMind最新研究：AI推理能力提升",
            "OpenAI研究：多模态AI融合",
            "Meta AI：模型可解释性研究",
            "微软：AI在生产力工具中的应用",
            "IBM：AI伦理和安全研究"
        ]

        return random.sample(research_papers, 1)

    def search_ai_news(self) -> List[str]:
        """搜索AI行业新闻"""
        self.log_message("🔍 搜索AI行业新闻...")

        # 模拟搜索结果
        ai_news = [
            "AI芯片市场增长预测",
            "AI监管政策最新进展",
            "AI在金融领域的应用",
            "AI教育平台发展趋势",
            "AI医疗诊断系统获批"
        ]

        return random.sample(ai_news, 1)

    def crawl_knowledge(self):
        """执行一次知识爬取任务"""
        self.log_message("🚀 开始AI知识爬取任务")

        all_knowledge = []

        try:
            # 搜索GitHub热门项目
            github_knowledge = self.search_github_trending()
            all_knowledge.extend(github_knowledge)

            # 搜索arXiv论文
            arxiv_knowledge = self.search_arxiv_papers()
            all_knowledge.extend(arxiv_knowledge)

            # 搜索技术博客
            tech_knowledge = self.search_tech_blogs()
            all_knowledge.extend(tech_knowledge)

            # 搜索研究机构论文
            research_knowledge = self.search_research_papers()
            all_knowledge.extend(research_knowledge)

            # 搜索AI新闻
            news_knowledge = self.search_ai_news()
            all_knowledge.extend(news_knowledge)

            # 保存知识到知识库
            self.save_knowledge(all_knowledge)

            self.log_message(f"✅ 知识爬取完成，共获取 {len(all_knowledge)} 条AI知识")

        except Exception as e:
            self.log_message(f"❌ 知识爬取失败：{e}")
            import traceback
            self.log_message(f"详细错误：{traceback.format_exc()}")

    def save_knowledge(self, knowledge_items: List[str]):
        """保存知识到知识库"""
        self.log_message(f"📚 保存 {len(knowledge_items)} 条知识到知识库...")

        # 加载知识库模块
        from knowledge_base import KnowledgeBase
        kb = KnowledgeBase()

        # 添加知识到知识库
        for i, knowledge in enumerate(knowledge_items):
            # 创建知识条目
            knowledge_entry = {
                "topic": knowledge,
                "category": "人工智能",
                "content": f"{knowledge} - 自动爬取的AI知识内容",
                "source": "自动爬虫",
                "keywords": ["AI", "人工智能", "机器学习", "深度学习"],
                "references": []
            }

            # 保存到知识库
            kb.learn_from_experience(knowledge_entry)

        self.log_message("✅ 知识保存完成")

    def run_crawler_schedule(self):
        """运行爬虫调度任务"""
        self.log_message("⏰ 启动爬虫调度器")

        # 每小时整点执行一次
        schedule.every().hour.at(":00").do(self.crawl_knowledge)

        # 立即执行一次作为测试
        self.crawl_knowledge()

        # 持续运行调度器
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次任务

    def start(self):
        """启动爬虫服务"""
        if self.is_running:
            self.log_message("⚠️  爬虫服务已经在运行中")
            return

        self.is_running = True

        # 创建并启动爬虫线程
        self.crawl_thread = threading.Thread(target=self.run_crawler_schedule, daemon=True)
        self.crawl_thread.start()

        self.log_message("✅ AI知识自动爬虫服务启动成功")
        self.log_message("📅 任务计划：每天每个小时整点执行一次AI知识搜索")
        self.log_message("💡 按 Ctrl+C 停止爬虫服务")

    def stop(self):
        """停止爬虫服务"""
        self.log_message("🛑 正在停止爬虫服务...")
        self.is_running = False

        if self.crawl_thread:
            self.crawl_thread.join(timeout=5)

        self.log_message("✅ 爬虫服务已停止")

    def get_crawler_status(self) -> Dict[str, Any]:
        """获取爬虫状态信息"""
        # 读取日志文件获取最近的活动记录
        log_file = os.path.join("data", "ai_knowledge_crawler.log")
        recent_logs = []

        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()[-10:]  # 最后10条日志
                recent_logs = [line.strip() for line in lines if line.strip()]

        return {
            "running": self.is_running,
            "next_run": self.get_next_run_time(),
            "knowledge_sources": self.knowledge_sources,
            "recent_logs": recent_logs
        }

    def get_next_run_time(self) -> str:
        """获取下一次运行时间"""
        now = datetime.datetime.now()
        next_hour = now.replace(microsecond=0, second=0, minute=0) + datetime.timedelta(hours=1)
        return next_hour.strftime("%Y-%m-%d %H:%M:%S")

def main():
    """主函数"""
    print("🤖 AI知识自动爬虫")
    print("=" * 60)

    crawler = AIKnowledgeCrawler()

    try:
        crawler.start()

        # 保持程序运行
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        crawler.log_message("⏹️  用户停止爬虫服务")
        crawler.stop()
        print("\n✅ 爬虫服务已停止")

if __name__ == "__main__":
    main()
