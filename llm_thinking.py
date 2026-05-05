#!/usr/bin/env python3
"""
🧠 LLM 思考增强 — 集成本地大模型到思考循环
通过 Hook 系统注册 4 个增强点，不修改核心循环代码。

设计模式：与 research_integration.py 完全一致的钩子注册方式。
每个钩子处理程序：check → build_context → call_llm → parse → merge
"""
import json
import logging
from typing import Any, Dict, List, Optional

from llm_client import get_llm_client, LLMResult
from llm_prompts import get_prompt

logger = logging.getLogger("llm_thinking")


class LLMThinkingIntegration:
    """
    LLM 思考增强器：通过 Hook 系统为 SelfThinkingAgent 注入 LLM 能力。

    注册 4 个钩子：
    - post_scan:      扫描后语义注释
    - post_questions: 问题完善
    - post_reflect:   反思深化
    - cycle_end:      周期综合
    """

    def __init__(self):
        self._client = None
        self._registered = False

    @property
    def client(self):
        if self._client is None:
            self._client = get_llm_client()
        return self._client

    def register_hooks(self, agent) -> bool:
        """注册 LLM 钩子到 SelfThinkingAgent，返回 LLM 是否可用"""
        available = self.client.is_available()
        if not available:
            print("  🤖 LLM 不可用，跳过 LLM 增强注册")
            return False

        agent.register_hook("post_scan", self._on_post_scan,
                            name="llm_on_scan", priority=5)
        # 问题完善在扫描后、算法处理前
        agent.register_hook("post_scan", self._on_post_questions_after_scan,
                            name="llm_on_questions", priority=15)
        agent.register_hook("post_reflect", self._on_post_reflect,
                            name="llm_on_reflect", priority=5)
        agent.register_hook("cycle_end", self._on_cycle_end,
                            name="llm_on_cycle_end", priority=10)

        self._registered = True
        print("  🤖 LLM 思考增强已注册 (POST_SCAN/POST_REFLECT/CYCLE_END)")
        return True

    # ── 钩子处理程序 ──

    def _on_post_scan(self, agent, **kw) -> None:
        """扫描后：LLM 语义注释"""
        if not self.client.is_available():
            return

        snapshot = getattr(agent, 'scan_result', None) or getattr(agent, '_last_scan', None)
        if not snapshot:
            return

        summary = self._summarize_snapshot(snapshot)
        if not summary:
            return

        prompt = get_prompt("scan_enhancement", snapshot_summary=summary)
        result = self.client.chat("你是一个简洁的代码分析助手。", prompt)

        if result.success and result.content.strip():
            notes = [line.strip() for line in result.content.split("\n")
                     if line.strip() and line.strip() != "无特别发现"]
            if notes:
                agent._llm_scan_notes = notes
                print(f"  🤖 LLM 扫描注释: {len(notes)} 条")

    def _on_post_questions_after_scan(self, agent, **kw) -> None:
        """扫描后：问题完善"""
        if not self.client.is_available():
            return

        # 等算法问题生成完再完善
        if not hasattr(agent, 'questions') or not agent.questions:
            return

        questions = agent.questions
        q_text = "\n".join(
            f"{getattr(q, 'importance', 0.5):.1f}|{q.question[:80]}|{getattr(q, 'target', '')}"
            for q in questions[:10]
        )
        snapshot = getattr(agent, 'scan_result', None) or {}
        strategy = getattr(agent, 'current_strategy_name', 'unknown')

        prompt = get_prompt(
            "question_refinement",
            questions_text=q_text,
            module_count=snapshot.get("total_files", 0),
            strategy=strategy,
            cycle_count=getattr(agent, 'cycle_count', 0),
        )
        result = self.client.chat("你是一个问题完善助手。保持简洁。", prompt)

        if not result.success or not result.content.strip():
            return
        if result.content.strip() == "无需修改":
            return

        # 解析完善后的问题
        enhanced = self._parse_questions(result.content)
        if enhanced:
            agent._llm_enhanced_questions = enhanced
            print(f"  🤖 LLM 完善了问题: {len(enhanced)} 条")

    def _on_post_reflect(self, agent, **kw) -> None:
        """反思后：LLM 深化元认知"""
        if not self.client.is_available():
            return

        current_insights = getattr(agent, 'last_insights', [])
        previous_insights = getattr(agent, 'prev_insights', [])
        current_questions = getattr(agent, 'questions', [])

        if not current_insights and not current_questions:
            return

        prompt = get_prompt(
            "reflection_enhancement",
            current_insights_summary=self._summarize_insights(current_insights),
            previous_insights_summary=self._summarize_insights(previous_insights),
            current_questions_summary="\n".join(
                q.question[:60] for q in current_questions[:5]
            ) if current_questions else "无",
            insight_count=len(current_insights),
            prev_insight_count=len(previous_insights),
            question_count=len(current_questions),
            prev_question_count=getattr(agent, 'prev_question_count', 0),
            strategy=getattr(agent, 'current_strategy_name', 'unknown'),
        )
        result = self.client.chat("你是一个元认知分析助手。保持简洁。", prompt)

        if result.success and result.content.strip():
            agent._llm_reflection = result.content.strip()
            print(f"  🤖 LLM 反思深化完成")

    def _on_cycle_end(self, agent, **kw) -> None:
        """周期结束：LLM 综合"""
        if not self.client.is_available():
            return

        insights = getattr(agent, 'insights', []) or getattr(agent, 'last_insights', [])
        if not insights:
            return

        i_text = "\n".join(
            f"- [{getattr(i, 'category', 'general')}] {getattr(i, 'content', str(i))[:100]}"
            for i in insights[:8]
        )
        actions = getattr(agent, '_last_actions', [])
        a_text = "\n".join(str(a) for a in actions[:5]) if actions else "无"
        kb_state = getattr(agent, '_kb_summary', '未知')

        prompt = get_prompt(
            "cycle_synthesis",
            insights_text=i_text,
            actions_text=a_text,
            knowledge_state=kb_state,
        )
        result = self.client.chat("你是一个知识综合助手。严格按 JSON 格式回复。", prompt)

        if result.success and result.content.strip():
            parsed = self._parse_json(result.content)
            if parsed:
                agent._llm_synthesis = parsed
                print(f"  🤖 LLM 周期综合完成")

    # ── 工具方法 ──

    def _summarize_snapshot(self, snapshot: Any) -> str:
        """从扫描快照提取摘要文本"""
        if isinstance(snapshot, dict):
            parts = []
            for k in ("total_files", "total_lines", "new_files", "large_modules",
                      "doc_coverage", "import_density"):
                v = snapshot.get(k)
                if v is not None:
                    parts.append(f"{k}: {v}")
            return "\n".join(parts) if parts else str(snapshot)[:300]
        return str(snapshot)[:300]

    def _summarize_insights(self, insights: List) -> str:
        """提取洞察摘要"""
        if not insights:
            return "无"
        lines = []
        for i in insights[:5]:
            if hasattr(i, 'content'):
                lines.append(i.content[:80])
            elif isinstance(i, dict):
                lines.append(str(i.get('content', str(i)))[:80])
            else:
                lines.append(str(i)[:80])
        return "\n".join(lines)

    def _parse_questions(self, text: str) -> List[Dict]:
        """解析 LLM 返回的问题列表"""
        questions = []
        for line in text.strip().split("\n"):
            line = line.strip()
            if "|" in line:
                parts = line.split("|", 2)
                try:
                    importance = float(parts[0])
                    question = parts[1] if len(parts) > 1 else ""
                    target = parts[2] if len(parts) > 2 else ""
                    questions.append({
                        "importance": importance,
                        "question": question,
                        "target": target,
                    })
                except (ValueError, IndexError):
                    continue
        return questions

    def _parse_json(self, text: str) -> Optional[Dict]:
        """尝试从 LLM 回复解析 JSON"""
        # 尝试直接解析
        text = text.strip()
        if text.startswith("{"):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
        # 尝试从 ```json 块提取
        if "```json" in text:
            try:
                start = text.index("```json") + 7
                end = text.index("```", start)
                return json.loads(text[start:end].strip())
            except (ValueError, json.JSONDecodeError):
                pass
        # 尝试从 ``` 块提取
        if "```" in text:
            try:
                start = text.index("```") + 3
                end = text.index("```", start)
                return json.loads(text[start:end].strip())
            except (ValueError, json.JSONDecodeError):
                pass
        logger.warning(f"无法解析 LLM JSON 回复: {text[:100]}")
        return None


def register_llm_hooks(agent) -> bool:
    """快捷入口：注册 LLM 钩子到 agent"""
    integration = LLMThinkingIntegration()
    return integration.register_hooks(agent)
