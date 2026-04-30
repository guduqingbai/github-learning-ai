#!/usr/bin/env python3
"""
📚 添加理论知识到知识库 - 提升自我思考和认知能力
"""

from knowledge_base import KnowledgeBase

def add_theory_knowledge():
    """添加更多理论知识到知识库"""
    kb = KnowledgeBase()

    # 新增理论知识条目（关于自我思考和认知科学）
    theory_knowledge = [
        {
            "topic": "自我意识理论",
            "category": "自我思考理论",
            "content": "自我意识是指个体对自身存在、思想和情感的认知。在人工智能中，实现自我意识需要系统能够反思自身状态、意图和行为。",
            "source": "认知科学百科全书",
            "keywords": ["自我意识", "认知科学", "人工智能", "反思"],
            "references": []
        },
        {
            "topic": "元认知理论",
            "category": "自我思考理论",
            "content": "元认知是对认知过程的认知，包括自我监控、自我调节和自我评估。AI元认知系统能够优化自身学习策略和推理过程。",
            "source": "元认知研究论文",
            "keywords": ["元认知", "自我监控", "自我调节", "学习策略"],
            "references": []
        },
        {
            "topic": "认知架构理论",
            "category": "自我思考理论",
            "content": "认知架构是模拟人类认知过程的计算框架，包括感知、记忆、推理和决策。常见架构有ACT-R、SOAR和CLUER。",
            "source": "认知架构研究",
            "keywords": ["认知架构", "ACT-R", "SOAR", "认知过程"],
            "references": []
        },
        {
            "topic": "自我反思机制",
            "category": "自我思考理论",
            "content": "自我反思是AI系统评估自身行为和决策的过程，通过分析成功与失败案例提升未来性能。",
            "source": "自我反思AI研究",
            "keywords": ["自我反思", "行为评估", "决策分析", "性能优化"],
            "references": []
        },
        {
            "topic": "自我学习理论",
            "category": "自我思考理论",
            "content": "自我学习系统能够自主识别学习需求、制定学习计划和评估学习效果，实现持续改进。",
            "source": "自主学习研究",
            "keywords": ["自我学习", "自主学习", "学习需求", "学习计划"],
            "references": []
        },
        {
            "topic": "自我决定理论",
            "category": "自我思考理论",
            "content": "自我决定理论强调人类行为的内在动机，包括自主、胜任和关联三个核心需求。AI系统可以模拟这些动机机制。",
            "source": "动机心理学",
            "keywords": ["自我决定", "内在动机", "自主", "胜任", "关联"],
            "references": []
        },
        {
            "topic": "认知失调理论",
            "category": "自我思考理论",
            "content": "认知失调是指信念和行为之间的不一致，导致心理不适。AI系统可以通过调整信念或行为来解决认知失调。",
            "source": "社会心理学",
            "keywords": ["认知失调", "信念调整", "行为改变", "心理不适"],
            "references": []
        },
        {
            "topic": "自我概念发展理论",
            "category": "自我思考理论",
            "content": "自我概念是个体对自身的认知和评价，包括自我形象、自我价值和自我认同。AI系统可以通过学习和经验发展自我概念。",
            "source": "发展心理学",
            "keywords": ["自我概念", "自我形象", "自我价值", "自我认同"],
            "references": []
        },
        {
            "topic": "认知负荷理论",
            "category": "自我思考理论",
            "content": "认知负荷是学习过程中工作记忆的负担，过高的认知负荷会影响学习效果。AI系统可以优化信息呈现方式降低认知负荷。",
            "source": "教育心理学",
            "keywords": ["认知负荷", "工作记忆", "信息呈现", "学习效果"],
            "references": []
        },
        {
            "topic": "自我调节学习理论",
            "category": "自我思考理论",
            "content": "自我调节学习是学习者主动管理学习过程的能力，包括目标设置、策略选择和监控评估。",
            "source": "学习科学",
            "keywords": ["自我调节学习", "目标设置", "策略选择", "监控评估"],
            "references": []
        },
        {
            "topic": "自我效能理论",
            "category": "自我思考理论",
            "content": "自我效能是个体对自身完成任务能力的信念，影响动机和行为。AI系统可以通过成功经验提升自我效能。",
            "source": "社会认知理论",
            "keywords": ["自我效能", "能力信念", "动机", "行为"],
            "references": []
        },
        {
            "topic": "认知灵活性理论",
            "category": "自我思考理论",
            "content": "认知灵活性是个体适应新情境和解决复杂问题的能力，AI系统可以通过学习多种策略提升认知灵活性。",
            "source": "认知心理学",
            "keywords": ["认知灵活性", "适应能力", "问题解决", "策略学习"],
            "references": []
        },
        {
            "topic": "自我认知发展理论",
            "category": "自我思考理论",
            "content": "自我认知发展是个体对自身认知过程的理解和监控能力的发展，AI系统可以通过元认知学习实现类似发展。",
            "source": "认知发展研究",
            "keywords": ["自我认知", "元认知", "认知发展", "监控能力"],
            "references": []
        },
        {
            "topic": "自主代理理论",
            "category": "自我思考理论",
            "content": "自主代理是能够独立行动、制定目标和学习的智能系统，具备自我思考和自我决策能力。",
            "source": "代理理论",
            "keywords": ["自主代理", "独立行动", "目标制定", "自我决策"],
            "references": []
        },
        {
            "topic": "意识计算理论",
            "category": "自我思考理论",
            "content": "意识计算理论尝试用计算模型解释意识现象，包括全局工作空间理论和信息整合理论。",
            "source": "意识研究",
            "keywords": ["意识计算", "全局工作空间", "信息整合", "计算模型"],
            "references": []
        },
        {
            "topic": "情感认知理论",
            "category": "自我思考理论",
            "content": "情感认知研究情绪如何影响认知过程，AI系统可以通过模拟情感机制提升决策质量。",
            "source": "情感计算",
            "keywords": ["情感认知", "情绪影响", "决策质量", "情感机制"],
            "references": []
        },
        {
            "topic": "认知偏差理论",
            "category": "自我思考理论",
            "content": "认知偏差是人类认知过程中的系统性错误，AI系统可以通过学习和监控避免类似偏差。",
            "source": "判断与决策研究",
            "keywords": ["认知偏差", "系统性错误", "判断", "决策"],
            "references": []
        },
        {
            "topic": "自我监督学习理论",
            "category": "自我思考理论",
            "content": "自我监督学习是AI系统通过未标记数据自主学习的方法，提升学习效率和数据利用能力。",
            "source": "机器学习研究",
            "keywords": ["自我监督学习", "未标记数据", "学习效率", "数据利用"],
            "references": []
        },
        {
            "topic": "认知模拟理论",
            "category": "自我思考理论",
            "content": "认知模拟是通过计算模型模拟人类认知过程，帮助理解和改进AI系统的认知能力。",
            "source": "认知建模",
            "keywords": ["认知模拟", "计算模型", "认知能力", "模型改进"],
            "references": []
        },
        {
            "topic": "自我思考系统架构",
            "category": "自我思考理论",
            "content": "自我思考系统架构包括感知模块、认知模块、决策模块和反思模块，实现完整的自我思考过程。",
            "source": "AI架构研究",
            "keywords": ["自我思考架构", "感知模块", "认知模块", "决策模块", "反思模块"],
            "references": []
        }
    ]

    # 添加知识到知识库
    print("🚀 开始添加理论知识到知识库...")
    added_count = 0

    for knowledge in theory_knowledge:
        if kb.learn_from_experience(knowledge):
            added_count += 1

    print(f"✅ 成功添加 {added_count} 条理论知识")

    # 检查更新后的统计
    stats = kb.get_statistics()
    category_breakdown = kb.get_category_breakdown()

    print(f"\n📊 更新后的知识统计:")
    print(f"总知识条目: {stats['total_items']}")
    print(f"知识类别: {stats['categories']}")
    print(f"知识主题: {stats['topics']}")
    print("类别分布:")
    for category, count in category_breakdown.items():
        print(f"  • {category}: {count} 条")

    # 检查理论知识和项目知识数量
    theory_count = 0
    project_count = 0
    for item in kb.get_all_knowledge():
        if '理论' in item.get('category', '') or '认知' in item.get('category', ''):
            theory_count += 1
        elif '项目' in item.get('category', '') or '实践' in item.get('category', ''):
            project_count += 1

    print(f"\n理论知识数量: {theory_count} 条")
    print(f"项目知识数量: {project_count} 条")

    return added_count

if __name__ == "__main__":
    print("🎯 理论知识添加工具")
    print("=" * 60)
    add_theory_knowledge()
