#!/usr/bin/env python3
"""
Claude Memory Bridge — 自主思考系统 → 星期八记忆的桥梁

在每轮思考循环完成后，读取系统最新状态（知识库/研究/自我修复），
与上次同步快照对比，有实质变化时写入 Claude 的持久化记忆文件。
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple


class ClaudeMemoryBridge:
    """记忆桥梁：系统状态 → Claude 持久记忆"""

    def __init__(self):
        self.data_dir = Path("data")
        self.memory_dir = Path.home() / ".claude" / "projects" / "C--Users----" / "memory"
        self.tracker_file = self.data_dir / "claude_memory_sync_tracker.json"
        self.max_index_entries = 5
        self.min_new_entries = 2  # 至少 N 条新知识才触发同步

    # ── 门控检查 ──

    def should_sync(self) -> bool:
        """检查是否有必要执行同步"""
        tracker = self._read_tracker()
        if tracker is None:
            return True  # 首次运行

        current = self._gather_state()
        last = tracker.get("state", {})

        # 检查是否有意义的变化
        if current.get("kb_total", 0) - last.get("kb_total", 0) >= self.min_new_entries:
            return True
        if current.get("research_count", 0) > last.get("research_count", 0):
            return True
        if current.get("heal_total", 0) > last.get("heal_total", 0):
            return True
        if current.get("cycle_count", 0) > last.get("cycle_count", 0) + 10:
            return True  # 跑了 10+ 轮还没同步，该心跳了

        # 超过 24 小时的心跳
        last_sync = tracker.get("last_sync", "")
        if last_sync:
            try:
                hours = (datetime.now() - datetime.fromisoformat(last_sync)).total_seconds() / 3600
                if hours >= 24:
                    return True
            except Exception:
                pass

        return False

    # ── 主同步逻辑 ──

    def sync(self) -> Dict[str, Any]:
        """
        执行同步：读取状态 → 生成记忆 → 更新索引

        Returns:
            dict: {"synced": bool, "memory_name": str, "reason": str}
        """
        self._ensure_memory_dir()

        state = self._gather_state()
        tracker = self._read_tracker()

        if tracker is not None:
            last = tracker.get("state", {})
            if state["kb_total"] == last.get("kb_total", -1) and \
               state["research_count"] == last.get("research_count", -1) and \
               state["heal_total"] == last.get("heal_total", -1) and \
               state["cycle_count"] == last.get("cycle_count", -1):
                return {"synced": False, "reason": "no_changes"}

        # 生成记忆文件
        date_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        memory_name = f"system_status_{date_tag}"
        body = self._build_memory_body(state)
        memory_file = self.memory_dir / f"{memory_name}.md"

        # 原子写入
        tmp = memory_file.with_suffix(".tmp")
        tmp.write_text(body, encoding="utf-8")
        os.replace(str(tmp), str(memory_file))

        # 更新 MEMORY.md
        self._update_memory_index(memory_name, f"系统状态快照 {date_tag[:8]}")

        # 更新追踪器
        self._write_tracker(memory_name, state)

        return {
            "synced": True,
            "memory_name": memory_name,
            "entries_count": state.get("kb_total", 0),
            "reason": "new_data",
        }

    # ── 状态采集 ──

    def _gather_state(self) -> Dict[str, Any]:
        """采集系统当前状态"""
        state = {
            "kb_total": 0,
            "kb_categories": {},
            "research_count": 0,
            "research_latest": None,
            "cycle_count": 0,
            "heal_total": 0,
            "heal_successes": 0,
            "kb_delta_since_sync": [],
        }

        # 1. 知识库统计
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            all_k = kb.get_all_knowledge()
            state["kb_total"] = len(all_k)
            for entry in all_k:
                cat = entry.get("category", "未分类")
                state["kb_categories"][cat] = state["kb_categories"].get(cat, 0) + 1

            # 对比上次追踪，找出新条目
            tracker = self._read_tracker()
            if tracker:
                known_topics = set(tracker.get("state", {}).get("kb_topics", []))
                current_topics = {e.get("topic", "") for e in all_k}
                new_topics = current_topics - known_topics
                # 只取高重要性新条目
                high_imp = []
                for e in all_k:
                    if e.get("topic", "") in new_topics and e.get("importance", 0) >= 0.5:
                        high_imp.append(e.get("topic", ""))
                state["kb_delta_since_sync"] = high_imp[:5]
        except Exception:
            pass

        # 2. 研究日志
        try:
            journal = self.data_dir / "research_journal.md"
            if journal.exists():
                content = journal.read_text(encoding="utf-8")
                entries = [e for e in content.split("\n## ") if e.strip()]
                state["research_count"] = len(entries)
                if entries:
                    last_entry = "## " + entries[-1]
                    state["research_latest"] = self._parse_research_entry(last_entry)
        except Exception:
            pass

        # 3. 健康统计
        try:
            health = self.data_dir / "daemon_health.json"
            if health.exists():
                h = json.loads(health.read_text(encoding="utf-8"))
                state["cycle_count"] = h.get("cycle_count", 0)
                state["heal_total"] = h.get("heal_attempts", 0)
                state["heal_successes"] = h.get("heal_successes", 0)
        except Exception:
            pass

        return state

    @staticmethod
    def _parse_research_entry(entry: str) -> Dict[str, str]:
        """从研究日志条目中提取关键信息"""
        result = {"topic": "", "date": "", "summary": ""}
        lines = entry.split("\n")
        for line in lines:
            if line.startswith("## 研究:"):
                result["topic"] = line.replace("## 研究:", "").strip()
            elif line.startswith("**时间**:"):
                result["date"] = line.replace("**时间**:", "").strip()[:10]
            elif line.startswith("**摘要**:"):
                result["summary"] = line.replace("**摘要**:", "").strip()[:100]
        return result

    # ── 记忆文件构建 ──

    def _build_memory_body(self, state: Dict[str, Any]) -> str:
        """构建 YAML frontmatter + markdown 的记忆文件体"""
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        date_tag = datetime.now().strftime("%Y-%m-%d")

        lines = [
            "---",
            f"name: 系统状态快照 {date_tag}",
            f"description: 自主思考系统的知识、研究和活动摘要（截至{date_tag}）",
            "type: project",
            "originSessionId: claude-memory-bridge",
            "---",
            "",
            f"# 系统状态快照 {date_tag}",
            "",
            "## 知识库概况",
            f"- 总条目: {state.get('kb_total', 0)}",
        ]

        categories = state.get("kb_categories", {})
        if categories:
            sorted_cats = sorted(categories.items(), key=lambda x: -x[1])
            cats_str = ", ".join(f"{k}({v})" for k, v in sorted_cats[:6])
            lines.append(f"- 知识分类: {len(categories)} 个")
            lines.append(f"- 主要分类: {cats_str}")

        delta = state.get("kb_delta_since_sync", [])
        if delta:
            lines.append(f"- 新增高价值知识: {'、'.join(delta[:3])}")
            if len(delta) > 3:
                lines.append(f"  ...等 {len(delta)} 条")

        lines.append("")
        lines.append("## 最新研究")
        research = state.get("research_latest")
        if research:
            lines.append(f"- **主题**: {research.get('topic', '未知')}")
            lines.append(f"- **日期**: {research.get('date', '未知')}")
            summary = research.get("summary", "")
            if summary:
                lines.append(f"- **摘要**: {summary}")
        else:
            lines.append("- 暂无研究记录")
        if state.get("research_count", 0) > 0:
            lines.append(f"- 研究报告总数: {state.get('research_count')}")

        lines.append("")
        lines.append("## 系统活动")
        lines.append(f"- 思考轮次: {state.get('cycle_count', 0)}")
        heals = state.get("heal_total", 0)
        if heals > 0:
            rate = state.get("heal_successes", 0) / heals * 100
            lines.append(f"- 自我修复: {heals} 次尝试，{state.get('heal_successes')} 次成功 ({rate:.0f}%)")
        else:
            lines.append("- 自我修复: 无")

        lines.append("")
        lines.append("**Why:** 让星期八在后续对话中了解自主思考系统的学习进展和研究成果。")
        lines.append("**How to apply:** 阅读此快照了解系统最近学到了什么新知识、进行了哪些研究、以及自我修复的状态。如果用户询问系统状态或学习进度，可参考此文件。")
        lines.append("")

        return "\n".join(lines)

    # ── MEMORY.md 索引管理 ──

    def _update_memory_index(self, memory_name: str, description: str):
        """在 MEMORY.md 中添加条目，清理旧的自动同步条目"""
        index_file = self.memory_dir / "MEMORY.md"
        lines = []
        if index_file.exists():
            lines = index_file.read_text(encoding="utf-8").splitlines()

        # 找到分区标记
        divider = "## Auto-Synced (Daemon Bridge)"
        divider_idx = None
        for i, line in enumerate(lines):
            if line.strip() == divider:
                divider_idx = i
                break

        # 如果没有分区，在末尾添加
        if divider_idx is None:
            if lines and lines[-1].strip():
                lines.append("")
            lines.append(divider)
            divider_idx = len(lines)
            lines.append("")  # 分区后空行

        # 收集分区内的条目
        auto_entries = []
        manual_lines = lines[:divider_idx + 1]  # 分区标记之前的行（含标记）
        for line in lines[divider_idx + 1:]:
            line_s = line.strip()
            if line_s.startswith("- ["):
                auto_entries.append(line_s)
            elif line_s == "":
                continue

        # 新条目和文件名互斥
        new_entry = f"- [{memory_name}]({memory_name}.md) — {description}"
        auto_entries = [e for e in auto_entries if memory_name not in e]
        auto_entries.append(new_entry)

        # 只保留最新的 max_index_entries 条
        if len(auto_entries) > self.max_index_entries:
            # 找出多余的文件名并删除文件
            removed = auto_entries[:-self.max_index_entries]
            auto_entries = auto_entries[-self.max_index_entries:]
            for entry in removed:
                fname = self._extract_filename(entry)
                if fname:
                    (self.memory_dir / fname).unlink(missing_ok=True)

        # 重建文件
        output = manual_lines + [""] + auto_entries + [""]
        index_file.write_text("\n".join(output), encoding="utf-8")

    @staticmethod
    def _extract_filename(entry: str) -> Optional[str]:
        """从 '- [name](file.md)' 中提取文件名"""
        if "](" in entry and entry.endswith(")"):
            return entry.split("](")[-1].rstrip(")")
        return None

    # ── 追踪器读写 ──

    def _read_tracker(self) -> Optional[Dict]:
        """读取同步追踪器"""
        if self.tracker_file.exists():
            try:
                return json.loads(self.tracker_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return None

    def _write_tracker(self, memory_name: str, state: Dict[str, Any]):
        """写入同步追踪器"""
        tracker = {
            "last_sync": datetime.now().isoformat(),
            "last_memory_name": memory_name,
            "state": {
                "kb_total": state.get("kb_total", 0),
                "kb_categories": state.get("kb_categories", {}),
                "kb_topics": list(state.get("kb_categories", {}).keys()),
                "research_count": state.get("research_count", 0),
                "cycle_count": state.get("cycle_count", 0),
                "heal_total": state.get("heal_total", 0),
                "heal_successes": state.get("heal_successes", 0),
            },
            "version": 1,
        }
        self.data_dir.mkdir(exist_ok=True)
        tmp = self.tracker_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(tracker, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(self.tracker_file))

    # ── 辅助方法 ──

    def _ensure_memory_dir(self):
        """确保记忆目录存在"""
        self.memory_dir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # 独立测试
    print("🧠 Claude Memory Bridge 测试")
    print("=" * 50)

    bridge = ClaudeMemoryBridge()

    # 测试 should_sync
    print(f"\nshould_sync: {bridge.should_sync()}")

    # 测试 gather_state
    state = bridge._gather_state()
    print(f"\n系统状态:")
    print(f"  知识库: {state['kb_total']} 条, {len(state['kb_categories'])} 分类")
    print(f"  研究: {state['research_count']} 篇")
    print(f"  轮次: {state['cycle_count']}")
    print(f"  修复: {state['heal_total']}次/{state['heal_successes']}成功")
    if state.get('kb_delta_since_sync'):
        print(f"  新增高价值: {state['kb_delta_since_sync']}")

    # 测试 memory 构建
    body = bridge._build_memory_body(state)
    print(f"\n记忆体大小: {len(body)} 字符")
    print("--- 预览前 10 行 ---")
    for line in body.split("\n")[:10]:
        print(f"  {line}")

    # 执行完整同步
    print(f"\n执行同步...")
    result = bridge.sync()
    print(f"  结果: {result}")

    if result.get("synced"):
        mem_file = bridge.memory_dir / f"{result['memory_name']}.md"
        print(f"  文件: {mem_file}")
        print(f"  存在: {mem_file.exists()}")

    print(f"\n✅ Claude Memory Bridge 测试完成")
