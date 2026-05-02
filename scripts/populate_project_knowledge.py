"""为知识库补充项目自身的知识条目"""
import json
from pathlib import Path

data_dir = Path("data")
kb_file = data_dir / "knowledge_base.json"

# 加载现有知识
with open(kb_file, encoding="utf-8") as f:
    kb = json.load(f)

existing_topics = {item["topic"] for item in kb}

project_knowledge = [
    {
        "topic": "github-learning-ai 项目概述",
        "category": "项目自身",
        "content": (
            "github-learning-ai 是一个基于数据驱动的智能学习系统，专注于自我学习、自我优化和持续改进。"
            "项目包含38个Python模块，约11800行代码，涵盖认知架构、持续学习、知识管理、"
            "爬虫系统、浏览器集成、代码分析等多个子系统。"
            "项目采用单例模式管理核心组件，使用JSON文件持久化状态，通过多线程实现后台学习。"
        ),
        "source": "项目自分析",
        "keywords": ["github-learning-ai", "智能学习系统", "自我优化", "项目概述"],
        "references": [{"name": "GitHub仓库", "url": "https://github.com/guduqingbai/github-learning-ai"}]
    },
    {
        "topic": "SystemStateManager 系统状态管理器",
        "category": "项目自身",
        "content": (
            "SystemStateManager是项目的统一状态管理模块，采用单例模式实现。"
            "管理9个状态模块：active(主动沟通)、continuous(持续学习)、cognitive(认知架构)、"
            "self_learning(自我学习)、jarvis(Jarvis系统)、learning(学习进度)、system(系统状态)、"
            "knowledge(知识库)、vulnerabilities(漏洞管理)。"
            "使用线程锁保证并发安全，支持延迟加载和缓存优化。"
        ),
        "source": "项目自分析",
        "keywords": ["SystemStateManager", "状态管理", "单例模式", "线程安全"],
        "references": [{"name": "源码", "url": "system_state_manager.py"}]
    },
    {
        "topic": "CognitiveArchitecture 认知架构系统",
        "category": "项目自身",
        "content": (
            "CognitiveArchitecture实现了类似人类的认知循环：感知(PerceptionSystem)→推理(ReasoningSystem)"
            "→决策→学习(LearningSystem)。感知系统负责接收外部信息，推理系统进行逻辑分析，"
            "学习系统从经验中提取知识。包含注意力机制、好奇心和创造力模拟。"
        ),
        "source": "项目自分析",
        "keywords": ["CognitiveArchitecture", "认知架构", "感知系统", "推理系统", "学习系统"],
        "references": [{"name": "源码", "url": "cognitive_architecture.py"}]
    },
    {
        "topic": "ContinuousLearningSystem 持续学习系统",
        "category": "项目自身",
        "content": (
            "ContinuousLearningSystem实现了自动发现和学习新知识的能力。"
            "通过调用GitHub API搜索热门项目、arXiv API获取最新论文、Wikipedia API作为补充，"
            "系统能自主选择学习资源并评估内容价值。学习频率动态调整(高5分钟/中10分钟/低15分钟)，"
            "新知识自动存入KnowledgeBase。"
        ),
        "source": "项目自分析",
        "keywords": ["ContinuousLearningSystem", "持续学习", "自动学习", "API爬取"],
        "references": [{"name": "源码", "url": "continuous_learning.py"}]
    },
    {
        "topic": "KnowledgeBase 知识管理系统",
        "category": "项目自身",
        "content": (
            "KnowledgeBase是项目的核心知识存储系统，采用单例模式实现。"
            "支持知识的增删改查、基于关键词和分类的检索、相关主题推理、"
            "以及从经验中学习。使用RLock保证并发安全，写操作采用临时文件+重命名防止数据损坏。"
            "当前存储135条知识条目，涵盖人工智能、数据科学、工程等多个领域。"
        ),
        "source": "项目自分析",
        "keywords": ["KnowledgeBase", "知识管理", "单例模式", "知识检索", "RLock"],
        "references": [{"name": "源码", "url": "knowledge_base.py"}]
    },
    {
        "topic": "AIKnowledgeCrawler AI知识爬虫",
        "category": "项目自身",
        "content": (
            "AIKnowledgeCrawler是一个多源AI知识爬虫，支持从GitHub、arXiv、Hacker News、"
            "Wikipedia、Reddit、百度百科、B站、百度热搜等8个平台自动爬取AI相关资讯。"
            "内置任务队列管理去重，使用加权评分评估内容价值，支持定时调度。"
            "爬取结果自动存入知识库和本地日志。"
        ),
        "source": "项目自分析",
        "keywords": ["AIKnowledgeCrawler", "爬虫", "GitHub", "arXiv", "知识采集"],
        "references": [{"name": "源码", "url": "ai_knowledge_crawler.py"}]
    },
    {
        "topic": "ActiveCommunicationAI 主动沟通系统",
        "category": "项目自身",
        "content": (
            "ActiveCommunicationAI实现了系统与用户的主动交互能力。"
            "能够根据学习状态和知识积累自动生成沟通内容，包括学习建议、项目推荐和进度汇报。"
            "支持情感识别和关系管理，根据用户响应类型调整沟通策略。"
        ),
        "source": "项目自分析",
        "keywords": ["ActiveCommunicationAI", "主动沟通", "人机交互", "情感识别"],
        "references": [{"name": "源码", "url": "active_communication.py"}]
    },
    {
        "topic": "BrowserIntegration 浏览器集成模块",
        "category": "项目自身",
        "content": (
            "BrowserIntegration提供了与Chrome、Firefox、Edge等主流浏览器的集成能力。"
            "通过Chrome DevTools Protocol收集网页浏览数据，分析内容与学习的相关性。"
            "支持浏览器配置管理、连接测试和实时状态监控。"
            "使用内存缓存优化配置读取性能。"
        ),
        "source": "项目自分析",
        "keywords": ["BrowserIntegration", "浏览器集成", "Chrome DevTools", "内容分析"],
        "references": [{"name": "源码", "url": "browser_integration.py"}]
    },
    {
        "topic": "BackgroundLearningService 后台学习服务",
        "category": "项目自身",
        "content": (
            "BackgroundLearningService实现了用户离线时的自动学习能力。"
            "通过监测用户交互状态(5分钟无交互视为离线)，自动启动持续学习会话。"
            "单次学习最长1小时，用户上线自动停止。支持信号处理和优雅关闭。"
        ),
        "source": "项目自分析",
        "keywords": ["BackgroundLearningService", "后台学习", "离线学习", "无人值守"],
        "references": [{"name": "源码", "url": "background_learning_service.py"}]
    },
    {
        "topic": "SelfLearningSystem 自我学习系统",
        "category": "项目自身",
        "content": (
            "SelfLearningSystem是系统的自我优化引擎，负责自我反思、"
            "知识获取评估和系统优化建议。通过持续分析自身的学习效果和知识结构，"
            "发现知识盲区并推动爬虫补充。"
        ),
        "source": "项目自分析",
        "keywords": ["SelfLearningSystem", "自我学习", "自我反思", "系统优化"],
        "references": [{"name": "源码", "url": "self_learning_system.py"}]
    },
    {
        "topic": "项目架构设计",
        "category": "项目自身",
        "content": (
            "github-learning-ai采用模块化架构设计，核心组件包括："
            "1) 认知层：CognitiveArchitecture实现类人认知循环；"
            "2) 学习层：ContinuousLearningSystem + SelfLearningSystem实现持续自我学习；"
            "3) 数据层：KnowledgeBase + SystemStateManager统一管理知识；"
            "4) 采集层：AIKnowledgeCrawler + CrawlerDaemon多源数据爬取；"
            "5) 交互层：ActiveCommunicationAI + BrowserIntegration连接用户与浏览器；"
            "6) 集成层：ClaudeCodeAdapter + OpenClawAdapter提供专业代码分析。"
            "状态管理统一走SystemStateManager单例，数据文件存储在data/目录。"
        ),
        "source": "项目自分析",
        "keywords": ["项目架构", "模块化", "认知层", "数据层", "采集层"],
        "references": [{"name": "架构文档", "url": "ARCHITECTURE.md"}]
    },
    {
        "topic": "爬虫调度系统",
        "category": "项目自身",
        "content": (
            "项目包含三个调度层级的爬取系统："
            "1) AIKnowledgeCrawler内置定时器，每分钟检查任务队列；"
            "2) CrawlerDaemon作为独立守护进程，支持多平台轮询采集；"
            "3) ContinuousLearningSystem作为后台学习循环，自动搜索和学习。"
            "三者协作实现全天候的知识采集和更新。"
        ),
        "source": "项目自分析",
        "keywords": ["爬虫调度", "定时任务", "知识采集", "CrawlerDaemon"],
        "references": [
            {"name": "AIKnowledgeCrawler", "url": "ai_knowledge_crawler.py"},
            {"name": "CrawlerDaemon", "url": "crawler_daemon.py"}
        ]
    },
]

# 过滤已存在的条目
new_items = [item for item in project_knowledge if item["topic"] not in existing_topics]

if new_items:
    kb.extend(new_items)
    with open(kb_file, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)
    print(f"✅ 添加了 {len(new_items)} 条项目自身知识条目")
    for item in new_items:
        print(f"   - {item['topic']}")
else:
    print("ℹ️  所有项目知识条目已存在")

print(f"\n📊 知识库总计: {len(kb)} 条")
