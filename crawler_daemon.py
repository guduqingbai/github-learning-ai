#!/usr/bin/env python3
"""
🎯 AI知识爬虫后台守护进程 - 真实数据版
"""

import os, sys, time, schedule, threading
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class CrawlerDaemon:
    """爬虫后台守护进程"""

    def __init__(self):
        self.is_running = False
        self.log_file = os.path.join("data", "crawler_daemon.log")
        self._log_buffer = []
        os.makedirs("data", exist_ok=True)

    def log(self, message):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{ts}] {message}"
        print(entry)
        self._log_buffer.append(entry + "\n")
        if len(self._log_buffer) >= 10:
            self._flush_log()

    def _flush_log(self):
        if not self._log_buffer:
            return
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.writelines(self._log_buffer)
        self._log_buffer.clear()

    def run_crawl_task(self):
        """执行爬取任务 - 委托给真实爬虫"""
        self.log("🚀 开始执行AI知识爬取任务")
        try:
            from ai_knowledge_crawler import AIKnowledgeCrawler
            crawler = AIKnowledgeCrawler()
            crawler.crawl_all()
            # 爬取完成后自动评估内容价值，触发深度学习
            if crawler.last_results:
                try:
                    from crawler_learning_bridge import process_crawler_results
                    result = process_crawler_results(crawler.last_results)
                    self.log(f"🔬 学习桥接: 评估{result['evaluated']}条, 学习{result['learned']}条, 深挖{result['deep_dives']}个主题")
                except Exception as e:
                    self.log(f"⚠️ 学习桥接失败: {e}")
            self.log("✅ 守护进程爬取任务完成")
        except Exception as e:
            self.log(f"❌ 任务执行失败: {e}")
            import traceback
            self.log(f"详细: {traceback.format_exc()}")

    def start_scheduler(self):
        schedule.every(2).hours.at(":30").do(self.run_crawl_task)
        self.log("⏰ 调度器已启动，每2小时半执行爬取")
        self.run_crawl_task()
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)

    def start(self):
        if self.is_running:
            self.log("⚠️ 服务已在运行")
            return
        self.is_running = True
        self.log("🎯 爬虫守护进程启动 (真实数据版)")
        t = threading.Thread(target=self.start_scheduler, daemon=True)
        t.start()
        self.log("✅ 服务启动成功")

    def stop(self):
        if not self.is_running:
            return
        self.log("🛑 正在停止守护进程...")
        self.is_running = False


def main():
    print("🎯 AI知识爬虫守护进程 (真实数据版)")
    print("=" * 60)
    daemon = CrawlerDaemon()
    daemon.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        daemon.stop()
        print("✅ 服务已停止")


if __name__ == "__main__":
    main()
