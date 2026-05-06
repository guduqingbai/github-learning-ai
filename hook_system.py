"""
🪝 Hook 系统 — 思考循环生命周期事件 + 结构化消息

从 self_thinking_agent.py 抽出，零依赖模块。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional


class HookEvent:
    """思考循环生命周期事件"""
    # 全局
    CYCLE_START = "cycle_start"
    CYCLE_END = "cycle_end"
    # 扫描
    PRE_SCAN = "pre_scan"
    POST_SCAN = "post_scan"
    # 学习
    PRE_STUDY = "pre_study"
    POST_STUDY = "post_study"
    # 评估
    PRE_EVALUATE = "pre_evaluate"
    POST_EVALUATE = "post_evaluate"
    # 自我认知
    PRE_AWARENESS = "pre_awareness"
    POST_AWARENESS = "post_awareness"
    # 整理
    PRE_CONSOLIDATE = "pre_consolidate"
    POST_CONSOLIDATE = "post_consolidate"
    # 反思
    PRE_REFLECT = "pre_reflect"
    POST_REFLECT = "post_reflect"
    # 问题生成
    PRE_QUESTIONS = "pre_questions"
    POST_QUESTIONS = "post_questions"
    # 探索
    PRE_EXPLORE = "pre_explore"
    POST_EXPLORE = "post_explore"


class Hook:
    """单个钩子：绑定到特定事件的处理函数"""

    def __init__(self, event: str, handler, *, name: str = "", priority: int = 0):
        self.event = event
        self.handler = handler
        self.name = name or getattr(handler, "__name__", "unnamed")
        self.priority = priority

    def __repr__(self):
        return f"Hook(event={self.event}, name={self.name}, priority={self.priority})"


@dataclass
class ContentBlock:
    """结构化的内容块：带类型的可查询数据单元"""
    type: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleMessage:
    """思考循环中的一条消息，包含角色和内容块列表"""
    role: str
    blocks: List[ContentBlock] = field(default_factory=list)
    timestamp: str = ""


def build_cycle_messages(*,
                         phase: str,
                         scan_data: Optional[Dict] = None,
                         study_data: Optional[List] = None,
                         evaluation: Optional[Dict] = None,
                         questions: Optional[List] = None,
                         insights: Optional[List] = None,
                         errors: Optional[List[str]] = None) -> List[CycleMessage]:
    """构建结构化的思考循环消息序列"""
    ts = datetime.now().isoformat()
    messages = []

    sys_blocks = [ContentBlock(type="phase", data={"phase": phase})]
    if scan_data:
        sys_blocks.append(ContentBlock(type="scan", data=scan_data))
    if study_data:
        sys_blocks.append(ContentBlock(type="study", data={"count": len(study_data), "topics": [s.get("topic", "")[:50] for s in study_data[:5]]}))
    if evaluation:
        sys_blocks.append(ContentBlock(type="evaluation", data=evaluation))
    messages.append(CycleMessage(role="system", blocks=sys_blocks, timestamp=ts))

    if questions:
        q_blocks = [ContentBlock(type="question", data={
            "text": q.question[:100],
            "action": q.explore_action,
            "target": q.target,
            "importance": q.importance,
        }) for q in questions[:10]]
        messages.append(CycleMessage(role="assistant", blocks=q_blocks, timestamp=ts))

    if insights:
        i_blocks = []
        for ins in insights:
            i_type = ins.get("action_taken", "insight")
            i_blocks.append(ContentBlock(type=i_type, data={
                "topic": ins.get("topic", ""),
                "summary": ins.get("summary", "")[:200],
            }))
        messages.append(CycleMessage(role="tool", blocks=i_blocks, timestamp=ts))

    if errors:
        messages.append(CycleMessage(role="tool", blocks=[ContentBlock(type="error", data={"errors": errors})], timestamp=ts))

    return messages
