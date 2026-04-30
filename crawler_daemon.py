#!/usr/bin/env python3
"""
🎯 AI知识爬虫后台运行版本
"""

import os
import sys
import time
import schedule
import threading
import datetime
import random
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class CrawlerDaemon:
    """爬虫后台运行类"""

    def __init__(self):
        self.is_running = False
        self.log_file = os.path.join("data", "crawler_daemon.log")
        os.makedirs("data", exist_ok=True)

    def log(self, message):
        """记录日志"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

    def simulate_knowledge_search(self):
        """模拟知识搜索"""
        knowledge_items = [
            "LLM微调框架：支持多种大语言模型的快速微调",
            "向量数据库：高性能的AI知识存储解决方案",
            "AI辅助编程：代码生成和修复工具",
            "计算机视觉库：图像处理和分析工具",
            "自然语言处理：文本分析和生成工具",
            "大语言模型上下文窗口扩展技术研究",
            "高效注意力机制在AI中的应用",
            "多模态AI融合方法",
            "AI模型压缩和加速技术",
            "联邦学习安全协议"
        ]

        return random.sample(knowledge_items, random.randint(3, 7))

    def save_knowledge(self, items):
        """保存知识到知识库"""
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()

            for item in items:
                entry = {
                    "topic": item,
                    "category": "人工智能",
                    "content": f"{item} - 自动爬取的AI知识内容",
                    "source": "自动爬虫",
                    "keywords": ["AI", "人工智能", "机器学习", "深度学习"],
                    "references": []
                }
                kb.learn_from_experience(entry)

            self.log(f"✅ 成功保存 {len(items)} 条知识")
            return True
        except Exception as e:
            self.log(f"❌ 保存知识失败: {e}")
            return False

    def run_crawl_task(self):
        """执行爬取任务"""
        self.log("🚀 开始执行AI知识爬取任务")

        try:
            # 模拟知识搜索
            knowledge = self.simulate_knowledge_search()

            # 保存到知识库
            self.save_knowledge(knowledge)

            self.log(f"✅ 知识爬取完成，获取 {len(knowledge)} 条新内容")

        except Exception as e:
            self.log(f"❌ 任务执行失败: {e}")
            import traceback
            self.log(f"详细错误: {traceback.format_exc()}")

    def start_scheduler(self):
        """启动调度器"""
        # 每小时整点执行
        schedule.every().hour.at(":00").do(self.run_crawl_task)

        self.log("⏰ 调度器已启动，每小时整点执行任务")

        # 立即执行一次测试
        self.run_crawl_task()

        # 持续运行
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

    def start(self):
        """启动后台服务"""
        if self.is_running:
            self.log("⚠️  服务已经在运行中")
            return

        self.is_running = True
        self.log("🎯 AI知识爬虫后台服务启动")

        # 启动调度器线程
        scheduler_thread = threading.Thread(target=self.start_scheduler, daemon=True)
        scheduler_thread.start()

        self.log("✅ 服务启动成功")

    def stop(self):
        """停止服务"""
        if not self.is_running:
            self.log("⚠️  服务未运行")
            return

        self.log("🛑 正在停止爬虫服务...")
        self.is_running = False

def main():
    """主函数"""
    print("🎯 AI知识爬虫后台服务")
    print("=" * 60)

    daemon = CrawlerDaemon()
    daemon.start()

    try:
        # 运行10分钟后自动停止（用于测试）
        time.sleep(600)
        daemon.stop()
        print("✅ 测试完成，服务已停止")

    except KeyboardInterrupt:
        daemon.stop()
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()
