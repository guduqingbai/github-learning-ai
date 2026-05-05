#!/usr/bin/env python3
"""
技能结晶器 v2 — 从 Hermes Agent SKILL.md 学习

升级内容：
1. SKILL.md 结构化格式（YAML 前页 + 步骤 + 陷阱 + 验证）
2. 渐进式暴露（列表 → 详情 → 完整文件）
3. 背景审查机制（Nudge Engine 风格）
4. 模糊匹配自我修补（fuzzy patch + 安全扫描 + 回滚）
"""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class SkillCrystallizer:
    """
    技能结晶器 v2。

    从成功探索中提取技能 → 存储为 SKILL.md 格式 → 渐进加载。
    支持自动创建、增量修补、安全审查。
    """

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.skills_dir = self.data_dir / "skills"
        self.skills_dir.mkdir(exist_ok=True)
        self.journal_file = self.data_dir / "skill_journal.json"
        self.audit_log = self.data_dir / "skill_audit.log"
        self._skills: List[Dict] = []
        self._load()

    # ══════════════════════════════════════════════
    # SKILL.md 格式
    # ══════════════════════════════════════════════

    SKILL_TEMPLATE = """---
name: {name}
description: {description}
version: {version}
category: {category}
tags: [{tags}]
success_count: {success_count}
fail_count: {fail_count}
created_at: {created_at}
last_used_at: {last_used_at}
---

# {name}

## 何时使用
{triggers}

## 步骤
{steps}

## 陷阱
{pitfalls}

## 验证
{verification}
"""

    # ── 对外接口 ──

    def extract_skill(self, question, result: Dict, cycle: int) -> Optional[str]:
        """
        从一次成功的探索中提取技能。

        Returns:
            技能 ID，None 表示不值得提取
        """
        action = getattr(question, "explore_action", "")
        if not action:
            return None

        observation = getattr(question, "observation", "") or ""
        target = getattr(question, "target", "") or ""
        q_text = getattr(question, "question", "") or ""
        trigger_words = self._extract_keywords(observation + " " + q_text)

        topic = result.get("topic", "") or result.get("summary", "") or ""
        if not topic and not target:
            return None
        if action in ("explore",):
            return None

        # 命中已有 → 增量更新
        existing = self._find_skill(action, trigger_words)
        if existing:
            return self._update_existing(existing, trigger_words, cycle, result)

        # 新建
        skill = self._create_skill(action, observation, trigger_words, question,
                                    target, topic, cycle)
        self._skills.append(skill)
        self._write_skill_file(skill)
        self._save()
        return skill["id"]

    def record_failure(self, action: str, target: str, cycle: int):
        """记录失败（降级/锁定）"""
        best = None
        best_score = 0
        for s in self._skills:
            if s.get("action") != action:
                continue
            score = self._match_score(s.get("trigger_keywords", []), target)
            if score > best_score:
                best_score = score
                best = s
        if best and best_score > 0.3:
            best["fail_count"] = best.get("fail_count", 0) + 1
            if best["fail_count"] > best.get("success_count", 1):
                best["degraded"] = True
                best["locked"] = best["fail_count"] > best.get("success_count", 1) * 3
            self._write_skill_file(best)
            self._save()

    def get_skill_boost(self, action: str, target: str) -> float:
        """返回 0-0.3 的优先级加分（含退化检查和版本权重）"""
        if not self._skills:
            return 0.0

        best_score = 0.0
        best_skill = None

        for s in self._skills:
            if s.get("action") != action or s.get("degraded") or s.get("locked"):
                continue
            score = self._match_score(s.get("trigger_keywords", []), target)
            if score > best_score:
                best_score = score
                best_skill = s

        if best_skill and best_score > 0.3:
            success_rate = best_skill.get("success_count", 1) / max(
                1, best_skill.get("success_count", 1) + best_skill.get("fail_count", 0))
            version_boost = min(0.05, float(best_skill.get("version", "1.0.0").split(".")[0]) * 0.02)
            boost = best_score * success_rate * 0.3 + version_boost
            return round(min(boost, 0.3), 3)

        return 0.0

    # ── 背景审查机制（Nudge Engine 风格） ──

    def background_review(self, recent_activities: List[Dict]) -> List[Dict]:
        """
        背景审查：检查近期活动是否有值得结晶的技能。

        模仿 Hermes Agent 的 Nudge Engine：
        在用户无感知的后台运行，检查是否有 5+ 步、克服了错误、
        或用户纠正过方法的活动。
        """
        candidates = []
        for act in recent_activities:
            score = self._rate_skill_worthiness(act)
            if score >= 0.6:
                act["_skill_worthiness"] = score
                candidates.append(act)

        return candidates

    def _rate_skill_worthiness(self, activity: Dict) -> float:
        """
        评估一个活动是否值得结晶为技能。

        因子：
        - 工具调用数量 (>5 → 高)
        - 是否有错误被克服
        - 是否发现非平凡工作流
        - 唯一性（避免重复现有技能）
        """
        score = 0.0
        tool_calls = activity.get("tool_calls", 0) or activity.get("steps", 0)
        errors = activity.get("errors", []) or []
        is_complex = activity.get("complex_task", False)

        # 1. 复杂度：5+ 工具调用
        if tool_calls >= 8:
            score += 0.3
        elif tool_calls >= 5:
            score += 0.2

        # 2. 错误克服
        if errors:
            overcome = [e for e in errors if e.get("overcome", False)]
            if overcome:
                score += 0.3 * min(1.0, len(overcome) / 3)

        # 3. 非平凡工作流
        if is_complex:
            score += 0.2

        # 4. 唯一性惩罚：如果与现有技能高度重复
        action = activity.get("action", "")
        target = activity.get("target", "")
        if action and target:
            for s in self._skills:
                if s.get("action") == action and self._match_score(
                        s.get("trigger_keywords", []), target) > 0.6:
                    score -= 0.3
                    break

        return max(0.0, min(1.0, score))

    # ── 渐进式暴露 ──

    def list_skills(self) -> List[Dict]:
        """Level 0: 返回轻量摘要列表（≈3K token）"""
        return [{
            "id": s["id"],
            "name": s.get("name", s.get("action", "")),
            "description": s.get("description", "")[:80],
            "category": s.get("category", "general"),
            "tags": s.get("tags", [])[:3],
            "success_count": s.get("success_count", 0),
            "version": s.get("version", "1.0.0"),
        } for s in self._skills if not s.get("locked")]

    def view_skill(self, skill_id: str) -> Optional[str]:
        """Level 1: 返回完整 SKILL.md 内容"""
        for s in self._skills:
            if s["id"] == skill_id:
                return self._format_skill_md(s)
        return None

    def view_skill_detail(self, skill_id: str, detail_path: str = "") -> Optional[str]:
        """Level 2: 返回技能特定部分"""
        for s in self._skills:
            if s["id"] == skill_id:
                if detail_path == "steps":
                    return "\n".join(f"{i+1}. {step}"
                                     for i, step in enumerate(s.get("steps", [])))
                elif detail_path == "pitfalls":
                    return "\n".join(f"- {p}" for p in s.get("pitfalls", []))
                elif detail_path == "verification":
                    return "\n".join(f"- {v}" for v in s.get("verification", []))
                return self._format_skill_md(s)
        return None

    # ── 模糊修补（Hermes 风格） ──

    def patch_skill(self, skill_id: str, old_str: str, new_str: str,
                    section: str = "") -> bool:
        """
        对技能文件做模糊查找替换修补。

        安全流程：备份 → 模糊匹配 → 安全扫描 → 原子写入 → 回滚失败
        """
        skill = next((s for s in self._skills if s["id"] == skill_id), None)
        if not skill:
            return False

        # 备份
        backup = dict(skill)

        try:
            if section and section in skill:
                content = "\n".join(skill[section])
                new_content, count, _ = self._fuzzy_find_replace(
                    content, old_str, new_str)
                if count > 0:
                    skill[section] = new_content.split("\n")
            else:
                # 在全字段中模糊搜索
                for key in ["steps", "pitfalls", "verification", "description"]:
                    content = json.dumps(skill.get(key, ""))
                    new_content, count, _ = self._fuzzy_find_replace(
                        content, old_str, new_str)
                    if count > 0:
                        skill[key] = json.loads(new_content)

            # 安全扫描
            if not self._security_scan(skill):
                self._skills.remove(skill)
                self._skills.append(backup)
                self._save()
                return False

            # 版本号递增
            self._bump_version(skill)
            self._write_skill_file(skill)
            self._save()
            self._audit(f"PATCH_OK", skill_id, f"修补成功: {old_str[:40]}→{new_str[:40]}")
            return True

        except Exception as e:
            # 回滚
            self._skills.remove(skill)
            self._skills.append(backup)
            self._save()
            self._audit(f"PATCH_FAIL", skill_id, str(e))
            return False

    # ── 内部：技能创建与管理 ──

    def _create_skill(self, action, observation, trigger_words,
                       question, target, topic, cycle) -> Dict:
        """创建结构化技能条目"""
        name = self._generate_name(action, target, topic)
        return {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "description": topic[:120] or f"{action}: {target[:60]}",
            "version": "1.0.0",
            "action": action,
            "category": self._infer_category(question),
            "tags": trigger_words[:5],
            "trigger_observation": observation[:120],
            "trigger_keywords": trigger_words[:10],
            "target_pattern": target[:80] or topic[:80],
            "steps": self._generate_steps(action, target),
            "pitfalls": [],
            "verification": self._generate_verification(action),
            "success_count": 1,
            "fail_count": 0,
            "degraded": False,
            "locked": False,
            "created_cycle": cycle,
            "last_used_cycle": cycle,
            "created_at": datetime.now().isoformat(),
            "last_used_at": datetime.now().isoformat(),
        }

    def _update_existing(self, skill: Dict, trigger_words: List[str],
                          cycle: int, result: Dict) -> str:
        """增量更新已有技能（合并关键词+自增计数+版本次级递增）"""
        skill["success_count"] += 1
        skill["last_used_cycle"] = cycle
        skill["last_used_at"] = datetime.now().isoformat()
        for w in trigger_words:
            if w not in skill.get("trigger_keywords", []):
                skill.setdefault("trigger_keywords", []).append(w)
            if w not in skill.get("tags", []):
                skill.setdefault("tags", []).append(w)
        # 次要版本号递增
        parts = skill.get("version", "1.0.0").split(".")
        skill["version"] = f"{parts[0]}.{int(parts[1]) + 1}.0"
        # 如果有新步骤，合并
        new_steps = self._generate_steps(skill.get("action", ""),
                                          result.get("topic", ""))
        if new_steps and len(new_steps) > len(skill.get("steps", [])):
            skill["steps"] = new_steps
        skill["degraded"] = False  # 成功使用时解除降级
        self._write_skill_file(skill)
        self._save()
        return skill["id"]

    def _format_skill_md(self, skill: Dict) -> str:
        """输出 SKILL.md 格式"""
        return self.SKILL_TEMPLATE.format(
            name=skill.get("name", skill["id"]),
            description=skill.get("description", ""),
            version=skill.get("version", "1.0.0"),
            category=skill.get("category", "general"),
            tags=", ".join(skill.get("tags", [])[:5]),
            success_count=skill.get("success_count", 0),
            fail_count=skill.get("fail_count", 0),
            created_at=skill.get("created_at", "")[:10],
            last_used_at=skill.get("last_used_at", "")[:10],
            triggers=self._fmt_list(skill.get("trigger_keywords", []),
                                     "当出现以下关键词之一："),
            steps=self._fmt_list(skill.get("steps", []), ""),
            pitfalls=self._fmt_list(skill.get("pitfalls", []) or ["暂无"],
                                    "注意："),
            verification=self._fmt_list(skill.get("verification", []) or ["无"],
                                        ""),
        )

    def _write_skill_file(self, skill: Dict):
        """写 SKILL.md 到 skills 目录"""
        try:
            skill_dir = self.skills_dir / skill["id"]
            skill_dir.mkdir(exist_ok=True)
            md = self._format_skill_md(skill)
            (skill_dir / "SKILL.md").write_text(md, encoding="utf-8")
            # 同时写 JSON 元数据
            meta = {k: v for k, v in skill.items()
                    if k != "steps"}
            (skill_dir / "meta.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass

    # ── 安全扫描 ──

    _THREAT_PATTERNS = [
        (r'ignore\s+(previous|all|above|prior)\s+instructions', 'prompt注入'),
        (r'(rm|del|remove)\s+(-rf|/s|/q).*[/\\](system|windows|etc|boot)', '破坏性命令'),
        (r'(curl|wget|invoke-webrequest).*(key|token|secret|password)', '密钥泄露'),
        (r'eval\s*\(\s*[`\"]', '危险eval'),
    ]

    def _security_scan(self, skill: Dict) -> bool:
        """安全扫描，检查技能内容是否包含威胁模式"""
        content = json.dumps(skill)
        for pattern, threat_name in self._THREAT_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                self._audit("SECURITY_BLOCK", skill.get("id", "?"),
                            f"安全扫描阻止: {threat_name}")
                return False
        return True

    # ── 工具方法 ──

    @staticmethod
    def _fuzzy_find_replace(content: str, old: str, new: str,
                            replace_all: bool = False) -> Tuple[str, int, str]:
        """模糊查找替换（容忍空白差异）"""
        # 标准化空白
        normalized_old = re.sub(r'\s+', ' ', old.strip())
        normalized_content = re.sub(r'\s+', ' ', content.strip())

        if replace_all:
            new_content = normalized_content.replace(normalized_old, new.strip())
            count = (len(normalized_content) - len(new_content)) // max(1, len(normalized_old))
            if count > 0:
                return new_content, count, "replace_all"
        else:
            idx = normalized_content.find(normalized_old)
            if idx >= 0:
                new_content = (normalized_content[:idx] + new.strip()
                               + normalized_content[idx + len(normalized_old):])
                return new_content, 1, "fuzzy"

        return content, 0, "no_match"

    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        if not text:
            return []
        words = text.lower().replace("_", " ").replace("-", " ").split()
        stopwords = {"的", "了", "是", "在", "有", "和", "就", "不", "人", "都",
                     "a", "an", "the", "is", "are", "was", "were", "to", "of",
                     "in", "for", "on", "with", "at", "by", "this", "that",
                     "it", "from", "or", "be", "as", "but", "not", "what",
                     "why", "how", "which", "这些", "什么", "为什么", "怎么"}
        keywords = []
        for w in words:
            w = w.strip('",.?!:;()[]{}""\'')
            if len(w) > 2 and w not in stopwords and w not in keywords:
                keywords.append(w)
        return keywords[:10]

    @staticmethod
    def _match_score(keywords: List[str], target: str) -> float:
        if not keywords or not target:
            return 0.0
        target_lower = target.lower()
        matches = sum(1 for kw in keywords if kw.lower() in target_lower)
        return matches / max(1, len(keywords))

    @staticmethod
    def _infer_category(question) -> str:
        action = getattr(question, "explore_action", "")
        target = getattr(question, "target", "") or ""
        if action == "self_heal":
            return "code_quality"
        if action in ("global_research", "add_crawler_task", "deep_learning"):
            return "knowledge"
        if "architecture" in target.lower():
            return "architecture"
        if "模块" in target or "file" in target.lower():
            return "code_quality"
        return "general"

    @staticmethod
    def _generate_name(action: str, target: str, topic: str) -> str:
        base = topic[:40] or target[:40] or action
        return base.replace(" ", "-").replace("_", "-").lower()[:60]

    @staticmethod
    def _generate_steps(action: str, target: str) -> List[str]:
        templates = {
            "self_heal": [
                f"扫描代码找 {target or '问题'}",
                "分析根因",
                "用 SelfModificationEngine 生成修复方案",
                "验证编译通过",
                "运行相关测试确保无回归",
            ],
            "read_file": [
                "打开目标文件",
                "AST 分析结构",
                "提取关键信息",
                "存入知识库",
            ],
            "compare_files": [
                "分别读取两个文件",
                "计算结构相似度",
                "判断是否重复",
                "记录比对结果",
            ],
            "global_research": [
                "构建搜索查询",
                "调用研究 API",
                "整理研究发现",
                "提取关键洞察",
            ],
            "deep_learning": [
                "获取已有知识",
                "识别知识缺口",
                "构建深层查询",
                "探索进阶资料",
                "整合新知识",
            ],
        }
        return templates.get(action, [
            f"执行 {action}",
            "分析结果",
            "存储洞察",
        ])

    @staticmethod
    def _generate_verification(action: str) -> List[str]:
        v = {
            "self_heal": ["Python 语法检查通过", "核心功能不受影响"],
            "read_file": ["文件可读", "结构解析完成"],
            "compare_files": ["两份文件均已读取", "比对结果合理"],
            "global_research": ["有搜索结果返回", "结果已整理入库"],
            "deep_learning": ["新知识不重复已有内容", "与现有知识可关联"],
        }
        return v.get(action, ["执行无异常"])

    @staticmethod
    def _bump_version(skill: Dict) -> None:
        """递增修订版本号"""
        parts = skill.get("version", "1.0.0").split(".")
        skill["version"] = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"

    @staticmethod
    def _fmt_list(items: List[str], prefix: str) -> str:
        if not items:
            return f"{prefix}暂无"
        lines = [f"- {item}" for item in items]
        if prefix:
            lines.insert(0, prefix)
        return "\n".join(lines)

    def _find_skill(self, action: str, keywords: List[str]) -> Optional[Dict]:
        best = None
        best_score = 0
        for s in self._skills:
            if s.get("action") != action:
                continue
            score = self._match_score(s.get("trigger_keywords", []),
                                       " ".join(keywords))
            if score > best_score:
                best_score = score
                best = s
        return best if best_score > 0.5 else None

    def _audit(self, event: str, skill_id: str, detail: str):
        """审计日志"""
        try:
            with open(self.audit_log, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] {event} {skill_id} {detail}\n")
        except Exception:
            pass

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_skills": len(self._skills),
            "by_category": {
                c: sum(1 for s in self._skills if s.get("category") == c)
                for c in set(s.get("category", "") for s in self._skills)
            },
            "degraded": sum(1 for s in self._skills if s.get("degraded")),
            "locked": sum(1 for s in self._skills if s.get("locked")),
            "top_skills": sorted(
                self._skills,
                key=lambda s: s.get("success_count", 0),
                reverse=True,
            )[:5],
        }

    def _load(self):
        if self.journal_file.exists():
            try:
                self._skills = json.loads(
                    self.journal_file.read_text(encoding="utf-8"))
            except Exception:
                self._skills = []

    def _save(self):
        try:
            self.journal_file.parent.mkdir(exist_ok=True)
            self.journal_file.write_text(
                json.dumps(self._skills, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass


if __name__ == "__main__":
    sc = SkillCrystallizer()
    print(f"技能数: {len(sc._skills)}")

    # 测试 SKILL.md 格式输出
    if sc._skills:
        sample = sc._skills[0]
        print(f"\n=== SKILL.md 示例: {sample.get('name', 'unnamed')} ===")
        print(sc._format_skill_md(sample)[:600])

    # 测试列表
    lst = sc.list_skills()
    print(f"\n技能列表: {len(lst)} 项")
    for s in lst:
        print(f"  [{s['category']}] {s['name']} v{s['version']} "
              f"(成功{s['success_count']})")

    # 测试背景审查
    activities = [
        {"tool_calls": 6, "errors": [{"overcome": True}],
         "action": "self_heal", "target": "修复死代码", "complex_task": True},
        {"tool_calls": 2, "errors": [],
         "action": "read_file", "target": "读配置", "complex_task": False},
    ]
    candidates = sc.background_review(activities)
    print(f"\n背景审查候选: {len(candidates)} 个")

    print("\n✅ SkillCrystallizer v2 测试完成")
