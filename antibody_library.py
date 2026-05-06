"""
🧬 抗体库 v3 — 策略升级 + 问题分诊
受用户启发：重要问题换策略修好，小问题放一放以后再想

每个抗体有多套 FixStrategy。对一个目标失败后自动升级到下一套策略。
重要性高的目标 → 试遍所有策略也要修好
重要性低的目标 → 试 1-2 次就暂缓
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable


# ── 一个修复策略 ─────────────────────────────────

class FixStrategy:
    """一种修复方案。一个抗体可以有多个策略，按顺序升级"""

    def __init__(self, name: str, description: str,
                 action: Callable, is_aggressive: bool = False):
        """__init__"""
        self.name = name
        self.description = description
        self.action = action          # (engine, target) → result
        self.is_aggressive = is_aggressive

    def execute(self, engine, target: str) -> Dict:
        """execute"""
        return self.action(engine, target)


# ── Buglog 修复档案（OpenWolf buglog.json 启发）──

class Buglog:
    """可搜索的 Bug 修复档案。修复成功后归档，下次遇到可以直接复用"""

    def __init__(self, data_dir: Path):
        """__init__"""
        self._file = Path(data_dir) / "buglog.json"
        self._entries: List[Dict] = []
        self._load()

    def _load(self):
        """_load"""
        if self._file.exists():
            try:
                self._entries = json.loads(self._file.read_text(encoding="utf-8"))
            except Exception:
                self._entries = []

    def _save(self):
        """_save"""
        try:
            self._file.parent.mkdir(parents=True, exist_ok=True)
            self._file.write_text(
                json.dumps(self._entries, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
        except Exception:
            pass

    def record_success(self, target: str, antibody_name: str,
                       strategy: str, detail: str = ""):
        """记录一次成功的修复"""
        entry = {
            "target": target,
            "antibody": antibody_name,
            "strategy": strategy,
            "detail": detail,
            "fixed_at": datetime.now().isoformat(),
            "fix_count": 1,
        }
        # 去重：同一文件 + 同一抗体视为已知修复，递增计数
        for existing in self._entries:
            if existing["target"] == target and existing["antibody"] == antibody_name:
                existing["fix_count"] += 1
                existing["last_fixed"] = datetime.now().isoformat()
                existing["strategy"] = strategy
                self._save()
                return
        self._entries.append(entry)
        if len(self._entries) > 100:  # 最多保留 100 条
            self._entries = self._entries[-100:]
        self._save()

    def search(self, target: str = "", antibody: str = "") -> List[Dict]:
        """搜索修复档案"""
        results = []
        for e in self._entries:
            if target and target not in e["target"]:
                continue
            if antibody and antibody != e["antibody"]:
                continue
            results.append(e)
        return results

    def has_known_fix(self, target: str, antibody_name: str) -> bool:
        """检查这个目标的这个抗体是否已有成功修复记录"""
        for e in self._entries:
            if e["target"] == target and e["antibody"] == antibody_name:
                return True
        return False

    def get_statistics(self) -> Dict:
        """get_statistics"""
        return {
            "total_fixes": len(self._entries),
            "unique_targets": len(set(e["target"] for e in self._entries)),
        }


# ── 问题分诊 ────────────────────────────────────

class ProblemTriage:
    """判断一个问题值不值得修、应该试多少次"""

    # 重要性阈值
    HIGH_IMPORTANCE = 0.7    # 必须修好，试所有策略
    MEDIUM_IMPORTANCE = 0.4  # 试两次，不行就暂缓
    # LOW < 0.4              # 试一次，不行就暂缓

    @staticmethod
    def max_strategies(importance: float) -> int:
        """根据重要性决定最多试几套策略"""
        if importance >= ProblemTriage.HIGH_IMPORTANCE:
            return 999  # 不限，试到所有策略用完
        elif importance >= ProblemTriage.MEDIUM_IMPORTANCE:
            return 2
        else:
            return 1

    @staticmethod
    def should_defer(importance: float, strategies_tried: int,
                     total_strategies: int) -> bool:
        """判断是否应该暂缓这个问题"""
        max_tries = ProblemTriage.max_strategies(importance)
        # 已经试够了，或者所有策略都试过了还没成功
        return strategies_tried >= max_tries or strategies_tried >= total_strategies


# ── 单个抗体 ────────────────────────────────────

class Antibody:
    """抗体：检测问题 → 多策略升级修复 → 经验回馈"""

    EXPERIENCE_MAX_SIZE = 30

    def __init__(
        self,
        name: str,
        description: str,
        triggers: List[tuple],
        strategies: List[FixStrategy],
        target_extractor: Optional[Callable] = None,
        verifier: Optional[Callable] = None,
    ):
        """__init__"""
        self.name = name
        self.description = description
        self.triggers = triggers
        self.strategies = strategies          # 策略列表（按升级顺序）
        self.target_extractor = target_extractor
        self.verifier = verifier
        self.is_active = True

        # 每个目标的策略状态 {target: current_strategy_index}
        self._target_strategy: Dict[str, int] = {}
        # 经验追踪
        self.experience: List[Dict] = []

    # ── 统计 ──

    @property
    def success_count(self) -> int:
        """success_count"""
        return sum(1 for e in self.experience if e["success"])

    @property
    def failure_count(self) -> int:
        """failure_count"""
        return sum(1 for e in self.experience if not e["success"])

    @property
    def total_attempts(self) -> int:
        """total_attempts"""
        return len(self.experience)

    @property
    def success_rate(self) -> float:
        """success_rate"""
        return self.success_count / self.total_attempts if self.total_attempts > 0 else 0.0

    @property
    def dominant_error(self) -> str:
        """dominant_error"""
        errors: Dict[str, int] = {}
        for e in self.experience:
            if not e["success"]:
                ek = e.get("error_kind", "unknown")
                errors[ek] = errors.get(ek, 0) + 1
        return max(errors, key=errors.get) if errors else ""

    # ── 匹配 ──

    def matches(self, findings: List[str], summary: str) -> bool:
        """matches"""
        if not self.is_active:
            return False
        for field, keyword in self.triggers:
            if field == "finding":
                if any(keyword in f for f in findings):
                    return True
            elif field == "summary":
                if keyword in summary:
                    return True
        return False

    # ── 核心：升级式修复 ──

    def _get_strategy_index(self, target: str) -> int:
        """获取当前目标试到第几个策略了"""
        return self._target_strategy.get(target, 0)

    def _next_strategy(self, target: str):
        """升级到下一个策略。超出范围表示所有策略已用完"""
        current = self._get_strategy_index(target)
        self._target_strategy[target] = current + 1

    def _reset_strategy(self, target: str):
        """成功后重置策略计数"""
        self._target_strategy.pop(target, None)

    def apply(self, engine, insight: Dict[str, Any]) -> Dict[str, Any]:
        """尝试修复：从当前策略开始，失败自动升级"""
        target = self.target_extractor(insight) if self.target_extractor else None
        if not target:
            return self._record("", False, error_kind="no_target",
                                error="无法提取目标", strategy="")

        importance = insight.get("importance", 0.5)
        strategy_idx = self._get_strategy_index(target)

        # 检查是否应该暂缓
        if ProblemTriage.should_defer(importance, strategy_idx, len(self.strategies)):
            return self._record(target, False, error_kind="deferred",
                                error=f"重要性 {importance}，暂缓等待新策略",
                                strategy="deferred",
                                importance=importance)

        # 执行当前策略
        strategy = self.strategies[strategy_idx]
        result = self._try_strategy(engine, target, strategy)

        if result.get("success"):
            self._reset_strategy(target)
            return result
        else:
            # 失败：升级策略
            self._next_strategy(target)
            next_idx = self._get_strategy_index(target)
            result["next_strategy"] = next_idx
            result["strategies_left"] = len(self.strategies) - next_idx
            result["escalated"] = True
            return result

    def _try_strategy(self, engine, target: str,
                      strategy: FixStrategy) -> Dict[str, Any]:
        """执行单个策略"""
        result = strategy.execute(engine, target)
        result = dict(result) if isinstance(result, dict) else {"success": False}

        # 验证
        if result.get("success") and self.verifier:
            verified = self.verifier(engine, target)
            if not verified:
                result["success"] = False
                result["error_kind"] = "verification_failed"
                result["error"] = "修复后验证未通过"
            result["verified"] = verified

        result["strategy"] = strategy.name
        self._record(target, result.get("success", False),
                     error_kind=result.get("error_kind", ""),
                     error=result.get("error", ""),
                     strategy=strategy.name)
        return result

    def _record(self, target: str, success: bool, *,
                error_kind: str = "", error: str = "",
                strategy: str = "", importance: float = 0.5):
        """记录一次修复尝试"""
        self.experience.append({
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "success": success,
            "error_kind": error_kind,
            "error": error,
            "strategy": strategy,
            "importance": importance,
        })
        if len(self.experience) > self.EXPERIENCE_MAX_SIZE:
            self.experience = self.experience[-self.EXPERIENCE_MAX_SIZE:]
        return {
            "success": success,
            "error_kind": error_kind,
            "error": error,
            "strategy": strategy,
        }

    # ── 状态 ──

    def to_dict(self) -> Dict:
        """to_dict"""
        return {
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "strategies": [s.name for s in self.strategies],
            "total_attempts": self.total_attempts,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "dominant_error": self.dominant_error,
            "target_strategy_state": dict(self._target_strategy),
            "recent_experience": self.experience[-5:],
        }


# ── 工具函数 ────────────────────────────────────

def _extract_file_from_insight(insight: Dict[str, Any]) -> Optional[str]:
    """_extract_file_from_insight"""
    topic = insight.get("topic", "")
    if not topic:
        return None
    for suffix in [" 模块分析", " 相似度分析", " 自我修复"]:
        if suffix in topic:
            name = topic.replace(suffix, "")
            for part in name.split(","):
                part = part.strip()
                py = Path(f"{part}.py") if not part.endswith(".py") else Path(part)
                if py.exists():
                    return str(py)
    return None


# ── 抗体库 ──────────────────────────────────────

class AntibodyLibrary:
    """抗体库：管理所有抗体及其策略升级"""

    def __init__(self, data_dir: Optional[Path] = None):
        """__init__"""
        self._antibodies: List[Antibody] = []
        self._data_dir = Path(data_dir) if data_dir else Path("data")
        self._experience_file = self._data_dir / "antibody_experience.json"

        # 暂缓队列：低重要性且尝试失败的 {target, antibody_name, reason, timestamp}
        self.deferred: List[Dict] = []

        # Buglog 修复档案
        self.buglog = Buglog(self._data_dir)

        self._load_builtin()
        self._load()

    def _load_builtin(self):
        """注册内置抗体及其策略链"""
        self.register(Antibody(
            name="add_docstring",
            description="为缺少文档字符串的函数/类/模块添加文档",
            triggers=[("finding", "文档缺失"), ("finding", "模块文档缺失")],
            strategies=[
                FixStrategy("engine_add_module_docstring", "使用引擎添加模块文档",
                            lambda e, t: e.add_module_docstring(t)),
                FixStrategy("engine_fix_docstrings", "使用引擎修复函数/类文档",
                            lambda e, t: e.fix_missing_docstrings(t)),
                FixStrategy("manual_docstring", "直接向文件写入模块文档字符串",
                            lambda e, t: _manual_add_docstring(e, t)),
            ],
            target_extractor=_extract_file_from_insight,
        ))
        self.register(Antibody(
            name="fix_bare_except",
            description="修复裸 except 语句",
            triggers=[("summary", "裸 except"), ("summary", "bare except")],
            strategies=[
                FixStrategy("engine_fix_bare_except", "使用引擎修复裸 except",
                            lambda e, t: e.fix_bare_excepts(t)),
            ],
            target_extractor=_extract_file_from_insight,
        ))
        self.register(Antibody(
            name="add_return_types",
            description="为函数添加 -> None 返回类型",
            triggers=[("finding", "类型提示"), ("finding", "缺少类型提示")],
            strategies=[
                FixStrategy("engine_fix_return_types", "使用引擎添加返回类型",
                            lambda e, t: e.fix_missing_return_types(t)),
            ],
            target_extractor=_extract_file_from_insight,
        ))

    # ── 持久化 ──

    def _load(self):
        """_load"""
        if not self._experience_file.exists():
            return
        try:
            data = json.loads(self._experience_file.read_text(encoding="utf-8"))
            # 恢复抗体经验
            for entry in data.get("antibodies", []):
                ab = self.get_by_name(entry.get("name"))
                if ab:
                    ab.experience = entry.get("experience", [])
                    ab.is_active = entry.get("is_active", True)
            # 恢复暂缓队列
            self.deferred = data.get("deferred", [])
        except Exception:
            pass

    def save_experience(self):
        """save_experience"""
        data = {
            "antibodies": [ab.to_dict() for ab in self._antibodies],
            "deferred": self.deferred,
        }
        try:
            self._data_dir.mkdir(parents=True, exist_ok=True)
            self._experience_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
        except Exception:
            pass

    def register(self, antibody: Antibody):
        """register"""
        self._antibodies.append(antibody)

    # ── 匹配 ──

    def match(self, findings: List[str], summary: str) -> List[Antibody]:
        """match"""
        return [ab for ab in self._antibodies if ab.matches(findings, summary)]

    def get_by_name(self, name: str) -> Optional[Antibody]:
        """get_by_name"""
        for ab in self._antibodies:
            if ab.name == name:
                return ab
        return None

    # ── 暂缓队列管理 ──

    def add_deferred(self, target: str, antibody_name: str,
                     importance: float, reason: str = ""):
        """把一个暂缓不修的问题加入队列"""
        # 去重
        for d in self.deferred:
            if d["target"] == target and d["antibody"] == antibody_name:
                d["deferred_count"] += 1
                d["last_deferred"] = datetime.now().isoformat()
                return
        self.deferred.append({
            "target": target,
            "antibody": antibody_name,
            "importance": importance,
            "reason": reason,
            "deferred_at": datetime.now().isoformat(),
            "deferred_count": 1,
            "last_deferred": datetime.now().isoformat(),
        })
        self.save_experience()

    def get_deferred_summary(self) -> str:
        """get_deferred_summary"""
        if not self.deferred:
            return "  (暂无暂缓问题)"
        lines = [f"  ⏸️ 暂缓问题: {len(self.deferred)} 个"]
        for d in self.deferred[-5:]:
            lines.append(f"    {d['target']}: {d['reason']} (暂缓 {d['deferred_count']} 次)")
        return "\n".join(lines)

    # ── 统计 ──

    def get_statistics(self) -> List[Dict]:
        """get_statistics"""
        return [ab.to_dict() for ab in self._antibodies]

    def get_summary(self) -> str:
        """get_summary"""
        lines = [f"🧬 抗体库: {len(self._antibodies)} 个"]
        for ab in self._antibodies:
            icon = "✅" if ab.is_active else "⛔"
            rate = f"{ab.success_rate:.0%}" if ab.total_attempts > 0 else "—"
            strat = f"策略: {len(ab.strategies)} 级" if len(ab.strategies) > 1 else "单策略"
            lines.append(
                f"  {icon} {ab.name} ({strat}) — "
                f"尝试 {ab.total_attempts}, 成功率 {rate}"
                + (f" 主要错误: {ab.dominant_error}" if ab.dominant_error else "")
            )
        return "\n".join(lines)


# ── 备用策略实现 ──

def _manual_add_docstring(engine, target: str) -> Dict[str, Any]:
    """备用策略：直接向 Python 文件写入模块 docstring"""
    try:
        path = Path(target)
        if not path.exists():
            return {"success": False, "error": "文件不存在", "error_kind": "file_not_found"}
        content = path.read_text(encoding="utf-8")
        # 检查是否已有 docstring
        stripped = content.lstrip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            return {"success": False, "error": "已有文档字符串", "error_kind": "already_exists"}
        # 从文件名生成 docstring
        module_name = path.stem
        docstring = f'"""{module_name} 模块"""\n\n'
        # 跳过 shebang
        lines = content.split("\n")
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            if i == 0 and line.startswith("#!"):
                new_lines.append(line)
                continue
            if not inserted:
                new_lines.append("")
                new_lines.append(docstring)
                inserted = True
            new_lines.append(line)
        if not inserted:
            new_lines.insert(0, docstring + "\n")
        path.write_text("\n".join(new_lines), encoding="utf-8")
        return {"success": True, "strategy": "manual_docstring"}
    except Exception as e:
        return {"success": False, "error": str(e), "error_kind": "execute_failed"}
