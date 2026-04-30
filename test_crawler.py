#!/usr/bin/env python3
"""
🧪 AI知识爬虫简单测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_crawler_core_functions():
    """测试爬虫核心功能"""
    print("🧪 AI知识爬虫核心功能测试")
    print("=" * 60)

    try:
        # 测试导入
        from ai_knowledge_crawler import AIKnowledgeCrawler
        print("✅ 爬虫模块导入成功")

        # 创建爬虫实例
        crawler = AIKnowledgeCrawler()
        print("✅ 爬虫实例创建成功")

        # 测试日志功能
        print("\n📝 测试日志功能：")
        crawler.log_message("测试日志消息")
        print("✅ 日志功能正常")

        # 测试搜索功能
        print("\n🔍 测试搜索功能：")
        github_result = crawler.search_github_trending()
        print(f"GitHub搜索结果: {len(github_result)}条")

        arxiv_result = crawler.search_arxiv_papers()
        print(f"arXiv搜索结果: {len(arxiv_result)}条")

        tech_result = crawler.search_tech_blogs()
        print(f"技术博客搜索结果: {len(tech_result)}条")

        research_result = crawler.search_research_papers()
        print(f"研究论文搜索结果: {len(research_result)}条")

        news_result = crawler.search_ai_news()
        print(f"AI新闻搜索结果: {len(news_result)}条")

        print("✅ 所有搜索功能正常")

        # 测试知识保存功能
        print("\n📚 测试知识保存功能：")
        test_knowledge = [
            "测试知识条目1",
            "测试知识条目2",
            "测试知识条目3"
        ]

        crawler.save_knowledge(test_knowledge)
        print("✅ 知识保存功能正常")

        print("\n🎉 爬虫核心功能测试全部通过！")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_crawler_core_functions()
    sys.exit(0 if success else 1)
