#!/usr/bin/env python3
"""
分层记忆系统 — 从 GenericAgent L0-L4 架构学习

渐进式记忆加载，按需提取，token 效率优先。
L0: 元规则（不可变核心）
L1: 索引层（快速路由）
L2: 全局事实（稳定知识）
L3: SOP/技能（结晶流程）
L4: 会话归档（近期上下文）
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class LayeredMemory:
    """
    五层记忆架构。

    核心原则：默认只加载 L1 索引，特定记忆按需加载。
    信息密度最大化（GenericAgent 的 Contextual Information Density Maximization）。
    """

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.memory_file = self.data_dir / "layered_memory.json"

        # 五层记忆
        self._layers: Dict[str, List[Dict]] = {
            "L0_meta_rules": [],     # 不可变 — 系统身份、行为边界
            "L1_insight_index": [],  # 最小索引 — 快速路由
            "L2_global_facts": [],   # 稳定知识 — 用户偏好、环境配置
            "L3_sops": [],           # SOP/技能 — 结晶流程
            "L4_session_archive": [],# 归档 — 近期会话上下文
        }
        self._load()

    # ── 层级定义 ──

    @property
    def META_RULES(self) -> List[Dict]:
        return self._layers["L0_meta_rules"]

    @property
    def INSIGHT_INDEX(self) -> List[Dict]:
        return self._layers["L1_insight_index"]

    @property
    def GLOBAL_FACTS(self) -> List[Dict]:
        return self._layers["L2_global_facts"]

    @property
    def SOPS(self) -> List[Dict]:
        return self._layers["L3_sops"]

    @property
    def SESSION_ARCHIVE(self) -> List[Dict]:
        return self._layers["L4_session_archive"]

    # ── 写入接口 ──

    def set_meta_rule(self, key: str, value: str) -> None:
        """设置元规则（去重后追加）"""
        self._dedup_add("L0_meta_rules", {"key": key, "value": value,
                                           "set_at": datetime.now().isoformat()})
        self._save()

    def add_to_index(self, topic: str, category: str,
                     summary: str, ref: str = "") -> None:
        """添加索引条目"""
        entry = {
            "topic": topic[:100],
            "category": category[:50],
            "summary": summary[:200],
            "ref": ref[:200],
            "added_at": datetime.now().isoformat(),
            "access_count": 0,
        }
        self._dedup_add("L1_insight_index", entry, key="topic")
        self._save()

    def add_fact(self, domain: str, fact: str,
                 confidence: float = 1.0) -> None:
        """添加全局事实"""
        self._dedup_add("L2_global_facts", {
            "domain": domain[:50],
            "fact": fact[:500],
            "confidence": min(1.0, max(0.0, confidence)),
            "added_at": datetime.now().isoformat(),
            "verified_count": 0,
        }, key="fact")
        self._save()

    def add_sop(self, name: str, steps: List[str],
                triggers: List[str], pitfalls: List[str] = None,
                verification: List[str] = None) -> str:
        """添加 SOP（标准操作流程），返回 sop_id"""
        sop_id = str(hash(name + datetime.now().isoformat()))[-12:]
        entry = {
            "sop_id": sop_id,
            "name": name[:100],
            "steps": steps,
            "triggers": triggers or [],
            "pitfalls": pitfalls or [],
            "verification": verification or [],
            "success_count": 0,
            "fail_count": 0,
            "created_at": datetime.now().isoformat(),
            "last_used_at": datetime.now().isoformat(),
        }
        self._dedup_add("L3_sops", entry, key="name")
        self._save()
        return sop_id

    def archive_session(self, session_data: Dict) -> None:
        """归档会话"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "data": session_data,
        }
        self._layers["L4_session_archive"].append(entry)
        # L4 只保留最近 50 条
        if len(self._layers["L4_session_archive"]) > 50:
            self._layers["L4_session_archive"] = self._layers["L4_session_archive"][-50:]
        self._save()

    # ── 读取接口（渐进加载） ──

    def get_loading_plan(self, task_type: str = "") -> Dict[str, bool]:
        """
        返回渐进加载计划：哪些层需要加载。

        默认总是加载 L0+L1（元规则+索引）。
        L2/L3/L4 按任务类型按需加载。
        """
        plan = {
            "L0_meta_rules": True,    # 总是加载
            "L1_insight_index": True, # 总是加载
            "L2_global_facts": False,  # 按需
            "L3_sops": False,          # 按需
            "L4_session_archive": False, # 按需
        }

        # 特定任务类型触发深层加载
        task_lower = task_type.lower()
        if any(kw in task_lower for kw in ["研究", "research", "学习", "learn"]):
            plan["L2_global_facts"] = True
        if any(kw in task_lower for kw in ["修复", "fix", "开发", "develop", "code"]):
            plan["L3_sops"] = True
        if any(kw in task_lower for kw in ["继续", "continue", "上下文", "context"]):
            plan["L4_session_archive"] = True

        return plan

    def get_context(self, task_type: str = "",
                    max_tokens: int = 3000) -> str:
        """
        生成记忆上下文字符串（用于系统提示词）。

        渐进加载：基础上下文 + 按需深层加载。
        """
        parts = []

        # L0: 元规则（精简）
        meta = self.META_RULES
        if meta:
            lines = [f"  - {m['key']}: {m['value'][:100]}" for m in meta[-5:]]
            parts.append("[元规则]\n" + "\n".join(lines))

        # L1: 索引摘要（精简）
        index = self.INSIGHT_INDEX
        if index:
            lines = [f"  - [{e['category']}] {e['topic'][:60]}"
                     for e in index[-10:]]
            parts.append("[知识索引]\n" + "\n".join(lines))

        plan = self.get_loading_plan(task_type)

        # L2: 全局事实
        if plan.get("L2_global_facts"):
            facts = self.GLOBAL_FACTS
            if facts:
                high_conf = [f for f in facts if f.get("confidence", 0) > 0.7]
                lines = [f"  - [{f['domain']}] {f['fact'][:150]}"
                         for f in high_conf[-5:]]
                parts.append("[全局事实]\n" + "\n".join(lines))

        # L3: SOP 列表（仅名称和触发词，不加载具体步骤）
        if plan.get("L3_sops"):
            sops = self.SOPS
            if sops:
                lines = [f"  - {s['name']} (触发: {', '.join(s['triggers'][:3])})"
                         for s in sops[-5:]]
                parts.append("[可用SOP]\n" + "\n".join(lines))

        # L4: 会话归档（仅最近摘要）
        if plan.get("L4_session_archive"):
            archive = self.SESSION_ARCHIVE
            if archive:
                recent = archive[-3:]
                lines = [f"  - {a['timestamp'][:19]}: {str(a['data'])[:100]}"
                         for a in recent]
                parts.append("[近期归档]\n" + "\n".join(lines))

        context = "\n\n".join(parts)
        # 按 token 预算截断（粗暴按字符算）
        if len(context) > max_tokens * 4:
            context = context[:max_tokens * 4] + "\n... (截断)"
        return context if context else ""

    # ── SOP 匹配和更新 ──

    def find_sop(self, task_desc: str) -> Optional[Dict]:
        """找最匹配的 SOP"""
        best = None
        best_score = 0
        desc_lower = task_desc.lower()

        for sop in self.SOPS:
            triggers = sop.get("triggers", [])
            score = sum(1 for t in triggers if t.lower() in desc_lower)
            if score > best_score:
                best_score = score
                best = sop

        if best_score > 0:
            return best
        return None

    def record_sop_result(self, sop_id: str, success: bool) -> None:
        """记录 SOP 执行结果"""
        for sop in self._layers["L3_sops"]:
            if sop.get("sop_id") == sop_id:
                if success:
                    sop["success_count"] = sop.get("success_count", 0) + 1
                else:
                    sop["fail_count"] = sop.get("fail_count", 0) + 1
                sop["last_used_at"] = datetime.now().isoformat()
                break
        self._save()

    def verify_fact(self, domain: str, fact: str) -> bool:
        """验证并增加事实置信度"""
        for entry in self._layers["L2_global_facts"]:
            if entry.get("domain") == domain and entry.get("fact") == fact:
                entry["verified_count"] = entry.get("verified_count", 0) + 1
                entry["confidence"] = min(1.0, entry["confidence"] + 0.05)
                self._save()
                return True
        return False

    # ── 内部 ──

    def _dedup_add(self, layer: str, entry: Dict, key: str = "key") -> None:
        """去重后添加（相同 key 覆盖）"""
        existing = self._layers[layer]
        for i, e in enumerate(existing):
            if e.get(key) == entry.get(key):
                existing[i] = entry
                return
        existing.append(entry)

    def get_stats(self) -> Dict[str, int]:
        """各层条目数统计"""
        return {k: len(v) for k, v in self._layers.items()}

    def _load(self):
        if self.memory_file.exists():
            try:
                data = json.loads(
                    self.memory_file.read_text(encoding="utf-8"))
                for layer in self._layers:
                    if layer in data:
                        self._layers[layer] = data[layer]
            except Exception:
                pass

    def _save(self):
        try:
            self.memory_file.write_text(
                json.dumps(self._layers, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass


if __name__ == "__main__":
    lm = LayeredMemory()

    # 测试元规则
    lm.set_meta_rule("identity", "星期八 — 自我思考AI系统")
    lm.set_meta_rule("behavior", "所有输出基于可观察的项目事实")

    # 测试索引
    lm.add_to_index("LLM微调框架", "人工智能",
                    "支持多种大语言模型的快速微调")
    lm.add_to_index("知识图谱构建", "架构",
                    "实体-关系-属性三元组存储")

    # 测试事实
    lm.add_fact("系统", "知识库共 1443 条目", confidence=0.9)

    # 测试 SOP
    lm.add_sop(
        name="修复裸 except",
        steps=["扫描代码找裸 except",
               "用 SelfModificationEngine 修复",
               "验证编译通过"],
        triggers=["bare except", "裸 except", "异常处理"],
        pitfalls=["不要修改 except 的原有逻辑"],
        verification=["python -c compile"],
    )

    # 测试渐进加载
    ctx = lm.get_context(task_type="修复bug")
    print(f"=== 修复上下文 ({len(ctx)} chars) ===")
    print(ctx[:500])
    print(f"\n=== 统计 === {lm.get_stats()}")
    print("✅ 分层记忆系统测试完成")
