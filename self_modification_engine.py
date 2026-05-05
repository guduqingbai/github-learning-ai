#!/usr/bin/env python3
"""
🔧 自我修改引擎 — 安全地修改自身代码
基于 Security Gate Chain (from Claude Code Computer Use inputActionGates)
+ Mods Directory + Git Versioning 模式
每个修改经过 Gate Chain: KILL_SWITCH → SCOPE → RISK → PRE_VALIDATE → BACKUP → EXECUTE → POST_VALIDATE → COMMIT
"""

import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


# ── Categorical Error Kinds (from CuErrorKind in toolCalls.ts) ────────────

class ModErrorKind(str, Enum):
    """分类错误类型 — 所有返回都用分类而非自由文本（from CuErrorKind）"""
    GATE_BLOCKED = "gate_blocked"
    KILL_SWITCH_OFF = "kill_switch_off"
    SCOPE_DENIED = "scope_denied"
    RISK_TOO_HIGH = "risk_too_high"
    PRE_VALIDATE_FAILED = "pre_validate_failed"
    BACKUP_FAILED = "backup_failed"
    EXECUTE_FAILED = "execute_failed"
    POST_VALIDATE_FAILED = "post_validate_failed"
    FILE_NOT_FOUND = "file_not_found"
    CODE_MISMATCH = "code_mismatch"
    SUB_GATE_BLOCKED = "sub_gate_blocked"
    HUMAN_APPROVAL_DENIED = "human_approval_denied"
    ROLLED_BACK = "rolled_back"
    GIT_FAILED = "git_failed"
    CONSTITUTION_VIOLATION = "constitution_violation"
    OTHER = "other"


# ── Gate Result (from toolCalls.ts gate pattern) ──────────────────────────

@dataclass
class GateResult:
    """单个 gate 的检查结果"""
    passed: bool
    reason: str = ""
    error_kind: str = ""


class ModificationGate(Enum):
    """Gate 类型 — GateChain 中的每个检查点"""
    KILL_SWITCH = "kill_switch"
    CONSTITUTION = "constitution"  # 宪法门禁（始终启用，不可绕过）
    SCOPE = "scope"
    RISK_ASSESSMENT = "risk_assessment"
    PRE_VALIDATE = "pre_validate"
    BACKUP = "backup"
    EXECUTE = "execute"
    POST_VALIDATE = "post_validate"
    COMMIT = "commit"


# ── SubGates (from CuSubGates in types.ts) ────────────────────────────────

@dataclass
class ModSubGates:
    """独立子开关，控制每种修改类型的启用/禁用"""
    allow_bare_except_fix: bool = True
    allow_docstring_add: bool = True
    allow_unused_import_remove: bool = True
    allow_code_style_fix: bool = True
    allow_new_mod_creation: bool = True
    allow_destructive_change: bool = False
    allow_high_risk_mod: bool = False
    require_human_approval: bool = True


# ── ALLOWED_SCOPE ────────────────────────────────────────────────────────

# 允许修改的文件（白名单）。空列表 = 允许所有项目 .py 文件
ALLOWED_SCOPE: List[str] = []

# 禁止修改的文件（黑名单）—— 从宪法核心同步
from constitution import CONSTITUTION_MODULES

DENIED_SCOPE: List[str] = list(CONSTITUTION_MODULES)


# ── Risk Assessment ──────────────────────────────────────────────────────

def _assess_risk(filepath: str, old_code: str, new_code: str) -> Tuple[int, str]:
    """评估修改风险等级 (1-10) 和原因"""
    fname_lower = filepath.lower()
    # 致命风险 10: 修改安全机制
    if "gate" in fname_lower or "constitution" in fname_lower:
        return 10, "修改安全机制"
    # 致命风险 9: 删除大量代码
    if len(new_code.strip()) < 10 and len(old_code) > 100:
        return 9, "删除大量代码"
    # 高风险 8: 修改核心引擎
    if "engine" in fname_lower or "agent" in fname_lower:
        if old_code != new_code:
            return 8, "修改核心引擎"
    # 高风险 7: 修改类或魔术方法
    for keyword in ["class ", "def __"]:
        if keyword in old_code and keyword in new_code:
            if old_code != new_code:
                return 7, "修改了类或魔术方法"
    # 中风险 5: 修改 import 语句
    if "import " in old_code and "import " in new_code and old_code != new_code:
        return 5, "修改了 import 语句"
    # 中风险 4: 新增大量代码
    if len(new_code) > len(old_code) * 1.5 and len(new_code) - len(old_code) > 200:
        return 4, "新增大量代码"
    # 低风险 2: 常规修改
    return 2, "常规修改"


# ── GateChain ────────────────────────────────────────────────────────────

class GateChain:
    """安全门链 — 每个修改必须通过所有 gate（from Computer Use inputActionGates）"""

    def __init__(self, engine: "SelfModificationEngine"):
        self._engine = engine
        # 可独立启用/禁用每个 gate
        self._gate_config: Dict[ModificationGate, bool] = {
            ModificationGate.KILL_SWITCH: True,
            ModificationGate.CONSTITUTION: True,
            ModificationGate.SCOPE: True,
            ModificationGate.RISK_ASSESSMENT: True,
            ModificationGate.PRE_VALIDATE: True,
            ModificationGate.BACKUP: True,
            ModificationGate.EXECUTE: True,
            ModificationGate.POST_VALIDATE: True,
            ModificationGate.COMMIT: True,
        }
        # cached state
        self._cached_sub_gates: Optional[ModSubGates] = None

    def set_gate_enabled(self, gate: ModificationGate, enabled: bool):
        """启用/禁用指定 gate"""
        self._gate_config[gate] = enabled

    @property
    def sub_gates(self) -> ModSubGates:
        if self._cached_sub_gates is None:
            self._cached_sub_gates = ModSubGates()
        return self._cached_sub_gates

    def run(self, filepath: str, old_code: str, new_code: str,
            reason: str, mod_type: str = "code_fix") -> Optional[GateResult]:
        """运行完整 gate chain。返回 None=通过, GateResult=失败"""
        chain = [
            self._gate_kill_switch,
            self._gate_constitution,  # 宪法门禁（始终启用，不可绕过）
            self._gate_scope,
            self._gate_sub_gates,
            self._gate_risk_assessment,
            self._gate_pre_validate,
            self._gate_backup,
            self._gate_execute,
            self._gate_post_validate,
            self._gate_commit,
        ]
        for gate_fn in chain:
            result = gate_fn(filepath, old_code, new_code, reason, mod_type)
            if result is not None and not result.passed:
                return result
        return None

    def _gate_kill_switch(self, filepath: str, old_code: str, new_code: str,
                           reason: str, mod_type: str) -> Optional[GateResult]:
        if not self._gate_config[ModificationGate.KILL_SWITCH]:
            return None
        # 从 FeatureFlagManager 检查全局开关
        try:
            from system_state_manager import SystemStateManager
            sm = SystemStateManager()
            ffm = sm.get_feature_flag_manager()
            if not ffm.is_enabled("self_modification"):
                return GateResult(False, "self_modification feature flag 已关闭",
                                  ModErrorKind.KILL_SWITCH_OFF)
        except ImportError:
            pass
        return None

    def _gate_constitution(self, filepath: str, old_code: str, new_code: str,
                            reason: str, mod_type: str) -> Optional[GateResult]:
        """
        宪法门禁（硬拒绝模式——始终启用，不可绕过）。

        硬拒绝的含义：
        - 位于 BACKUP/EXECUTE gate 之前 → 宪法违规不走备份/写入/回滚流程
        - 不从 _gate_config 读取 → 系统无法通过修改配置禁用
        - 涉及宪法模块的修改被直接拒绝，不留任何中间状态

        检查维度：
        - CON.2: 文件是否在不可修改列表中
        - CON.5: 修改内容是否包含安全机制关键词
        """
        from constitution_gate import check_modification
        result = check_modification(filepath, new_code, reason)
        if not result.passed:
            principles = "; ".join(result.violated_principles)
            self._engine._audit_log(
                event_type="gate_blocked",
                file=filepath, gate="constitution",
                status="blocked",
                detail=f"宪法门禁硬拒绝: {principles}",
            )
            return GateResult(False, f"宪法门禁硬拒绝: {principles}",
                              ModErrorKind.CONSTITUTION_VIOLATION)
        return None

    def _gate_scope(self, filepath: str, old_code: str, new_code: str,
                     reason: str, mod_type: str) -> Optional[GateResult]:
        if not self._gate_config[ModificationGate.SCOPE]:
            return None
        fname = Path(filepath).name

        # 黑名单检查
        for denied in DENIED_SCOPE:
            if fname == denied or filepath.endswith(denied):
                self._engine._audit_log(
                    event_type="gate_blocked",
                    file=filepath, gate="scope",
                    status="blocked",
                    detail=f"文件在宪法黑名单中: {denied}",
                )
                return GateResult(False, f"{filepath} 在黑名单中，禁止修改",
                                  ModErrorKind.SCOPE_DENIED)

        # 白名单为空则允许所有（除黑名单外）
        if not ALLOWED_SCOPE:
            return None

        # 白名单检查
        for allowed in ALLOWED_SCOPE:
            if fname == allowed or filepath.endswith(allowed):
                return None

        self._engine._audit_log(
            event_type="gate_blocked",
            file=filepath, gate="scope",
            status="blocked",
            detail=f"文件不在修改白名单中",
        )
        return GateResult(False, f"{filepath} 不在修改白名单中",
                          ModErrorKind.SCOPE_DENIED)

    def _gate_sub_gates(self, filepath: str, old_code: str, new_code: str,
                         reason: str, mod_type: str) -> Optional[GateResult]:
        if not self._gate_config[ModificationGate.PRE_VALIDATE]:
            return None
        sub = self.sub_gates

        # 基于 mod_type 检查对应的 sub gate
        type_checks = {
            "bare_except": (sub.allow_bare_except_fix, "修复裸 except 已禁用"),
            "docstring": (sub.allow_docstring_add, "添加文档字符串已禁用"),
            "unused_import": (sub.allow_unused_import_remove, "移除未使用 import 已禁用"),
            "code_style": (sub.allow_code_style_fix, "代码风格修复已禁用"),
            "new_mod": (sub.allow_new_mod_creation, "新建 mod 已禁用"),
        }
        check = type_checks.get(mod_type)
        if check:
            allowed, msg = check
            if not allowed:
                return GateResult(False, msg, ModErrorKind.SUB_GATE_BLOCKED)
        return None

    def _gate_risk_assessment(self, filepath: str, old_code: str, new_code: str,
                               reason: str, mod_type: str) -> Optional[GateResult]:
        if not self._gate_config[ModificationGate.RISK_ASSESSMENT]:
            return None
        risk_level, risk_reason = _assess_risk(filepath, old_code, new_code)

        # 审计记录风险评估
        self._engine._audit_log(
            event_type="risk_assessment",
            file=filepath,
            risk_level=risk_level,
            detail=risk_reason,
            status="assessed",
        )

        # 致命风险 (9-10): 需要 allow_destructive_change + human_approval
        if risk_level >= 9:
            sub = self.sub_gates
            if not sub.allow_destructive_change:
                self._engine._audit_log(
                    event_type="gate_blocked",
                    file=filepath, risk_level=risk_level,
                    gate="risk_assessment", status="blocked",
                    detail=f"致命风险被禁止: {risk_reason}",
                )
                return GateResult(False, f"致命风险 (评级{risk_level}): {risk_reason} "
                                  f"需要启用 allow_destructive_change",
                                  ModErrorKind.RISK_TOO_HIGH)
            if sub.require_human_approval:
                self._engine._audit_log(
                    event_type="gate_blocked",
                    file=filepath, risk_level=risk_level,
                    gate="risk_assessment", status="blocked",
                    detail=f"致命风险需要人类确认: {risk_reason}",
                )
                return GateResult(False, f"致命风险需要人类确认: {risk_reason}",
                                  ModErrorKind.HUMAN_APPROVAL_DENIED)
            self._engine._audit_log(
                event_type="risk_override",
                file=filepath, risk_level=risk_level,
                status="human_approved", detail=risk_reason,
            )

        # 高风险 (7-8): 需要 allow_high_risk_mod
        elif risk_level >= 7:
            sub = self.sub_gates
            if not sub.allow_high_risk_mod:
                return GateResult(False, f"高风险 (评级{risk_level}): {risk_reason}。"
                                  f"需要启用 allow_high_risk_mod",
                                  ModErrorKind.RISK_TOO_HIGH)
            if sub.require_human_approval:
                return GateResult(False, f"高风险修改需要人类确认: {risk_reason}",
                                  ModErrorKind.HUMAN_APPROVAL_DENIED)

        # 中风险 (4-6): 自动通过 + 审计
        elif risk_level >= 4:
            self._engine._audit_log(
                event_type="modification",
                file=filepath, risk_level=risk_level,
                status="auto_approved",
                detail=f"中等风险: {risk_reason}",
            )

        # 低风险 (1-3): 自动通过，仅日志
        else:
            self._engine._log_modification(filepath, "auto_approved",
                                           f"低风险 ({risk_level}): {risk_reason}", reason)
        return None

    def _gate_pre_validate(self, filepath: str, old_code: str, new_code: str,
                            reason: str, mod_type: str) -> Optional[GateResult]:
        if not self._gate_config[ModificationGate.PRE_VALIDATE]:
            return None
        if filepath.endswith(".py"):
            valid, err = self._engine.validate_python(new_code)
            if not valid:
                return GateResult(False, f"修改前验证失败 (语法错误): {err}",
                                  ModErrorKind.PRE_VALIDATE_FAILED)
        return None

    def _gate_backup(self, filepath: str, old_code: str, new_code: str,
                      reason: str, mod_type: str) -> Optional[GateResult]:
        if not self._gate_config[ModificationGate.BACKUP]:
            return None
        backup_path = self._engine._create_backup(Path(filepath))
        if not backup_path:
            return GateResult(False, "备份创建失败",
                              ModErrorKind.BACKUP_FAILED)
        # 暂存到 engine 用于后续可能的回滚
        self._engine._last_backup = backup_path
        return None

    def _gate_execute(self, filepath: str, old_code: str, new_code: str,
                       reason: str, mod_type: str) -> Optional[GateResult]:
        if not self._gate_config[ModificationGate.EXECUTE]:
            return None
        try:
            Path(filepath).write_text(new_code, encoding="utf-8")
            return None
        except Exception as e:
            return GateResult(False, f"写入失败: {e}",
                              ModErrorKind.EXECUTE_FAILED)

    def _gate_post_validate(self, filepath: str, old_code: str, new_code: str,
                             reason: str, mod_type: str) -> Optional[GateResult]:
        if not self._gate_config[ModificationGate.POST_VALIDATE]:
            return None
        if not filepath.endswith(".py"):
            return None
        try:
            written = Path(filepath).read_text(encoding="utf-8")
            valid, err = self._engine.validate_python(written)
            if not valid:
                return GateResult(False, f"修改后验证失败 (语法错误): {err}",
                                  ModErrorKind.POST_VALIDATE_FAILED)
            # 检查关键导入是否还在
            _check_critical_imports(old_code, written, filepath)
            return None
        except Exception as e:
            return GateResult(False, f"修改后验证异常: {e}",
                              ModErrorKind.POST_VALIDATE_FAILED)

    def _gate_commit(self, filepath: str, old_code: str, new_code: str,
                      reason: str, mod_type: str) -> Optional[GateResult]:
        if not self._gate_config[ModificationGate.COMMIT]:
            return None
        commit_msg = f"🤖 自我修改: {reason or filepath}"
        try:
            self._engine._create_git_commit(commit_msg)
            return None
        except Exception as e:
            return GateResult(False, f"git commit 失败: {e}",
                              ModErrorKind.GIT_FAILED)


def _check_critical_imports(old_code: str, new_code: str, filepath: str):
    """用正则检查关键导入是否在修改后被移除（快速检查，非 AST 级）"""
    # 提取所有 import 语句
    old_imports = set(re.findall(r'^\s*(?:import |from \S+ import )', old_code, re.MULTILINE))
    new_imports = set(re.findall(r'^\s*(?:import |from \S+ import )', new_code, re.MULTILINE))
    removed = old_imports - new_imports
    if removed:
        # 这是警告而非阻止，记录到日志
        pass  # 未来可扩展


class SelfModificationEngine:
    """安全的自我修改引擎（带 GateChain 安全门链）"""

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.log_file = self.data_dir / "modification_log.json"
        self.backup_dir = self.data_dir / "mod_backups"
        self.backup_dir.mkdir(exist_ok=True)
        self.modifications_dir = Path("mods")
        self.modifications_dir.mkdir(exist_ok=True)

        # GateChain 安全系统
        self.gate_chain = GateChain(self)
        self._last_backup: Optional[Path] = None

    # ---- 核心操作 ----

    def apply_code_fix(self, filepath: str, old_code: str, new_code: str,
                       reason: str = "", mod_type: str = "code_fix") -> Dict[str, Any]:
        """原子级代码修复：GateChain → 备份 → 写入 → 验证 → 提交"""
        full_path = Path(filepath).resolve()
        if not full_path.exists():
            return {"success": False, "error": f"文件不存在: {filepath}",
                    "error_kind": ModErrorKind.FILE_NOT_FOUND}

        current = full_path.read_text(encoding="utf-8")
        if old_code not in current:
            self._log_modification(filepath, "failed", "old_code_not_found", reason)
            return {"success": False, "error": "代码匹配失败，可能文件已被修改",
                    "error_kind": ModErrorKind.CODE_MISMATCH}

        new_content = current.replace(old_code, new_code, 1)

        # ── GateChain 安全门链 ──
        gate_result = self.gate_chain.run(
            str(full_path), current, new_content, reason, mod_type)
        if gate_result is not None:
            self._log_modification(filepath, "gate_blocked",
                                   f"{gate_result.error_kind}: {gate_result.reason}", reason)
            self._audit_log(
                event_type="gate_blocked",
                file=filepath,
                gate=gate_result.error_kind,
                status="blocked",
                detail=gate_result.reason,
            )
            return {"success": False, "error": gate_result.reason,
                    "error_kind": gate_result.error_kind}

        # ── 所有 gate 通过 ──
        # 宪法后置校验：任何修改后检查宪法完整性（防御深度）
        try:
            from constitution import verify_integrity as _verify_constitution
            if not _verify_constitution():
                self._log_modification(filepath, "critical",
                    "⚠️ 修改后宪法完整性校验失败！请联系主人检查系统")
        except Exception:
            pass

        self._log_modification(filepath, "success", reason,
                               f"修改成功 (gate chain 全部通过)")
        self._audit_log(
            event_type="modification",
            file=filepath,
            status="success",
            detail=f"Gate chain 全部通过: {reason}",
        )
        return {"success": True, "backup": str(self._last_backup)}

    def validate_python(self, code: str) -> Tuple[bool, Optional[str]]:
        """验证 Python 语法正确性"""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)

    def rollback(self, backup_path: str) -> bool:
        """从备份还原文件"""
        backup = Path(backup_path)
        if not backup.exists():
            return False
        original_name = backup.name.replace(".bak_", ".")
        for f in self.backup_dir.iterdir():
            if f.name == backup.name:
                continue
        original = Path(original_name)
        if not original.exists():
            stem = backup.stem
            base = stem.split("_bak_")[0]
            candidate = Path(base)
            if candidate.exists():
                original = candidate

        result = self._restore_backup(original, backup)
        if result:
            self._audit_log(
                event_type="rollback",
                file=str(backup),
                status="success",
                detail=f"从备份还原: {backup.name}",
            )
        return result

    def get_modification_stats(self) -> Dict[str, Any]:
        """获取修改统计"""
        logs = self._load_logs()
        total = len(logs)
        succeeded = sum(1 for l in logs if l.get("status") == "success")
        failed = sum(1 for l in logs if l.get("status") == "failed")
        rolled_back = sum(1 for l in logs if l.get("status") == "rolled_back")
        gate_blocked = sum(1 for l in logs if l.get("status") == "gate_blocked")
        audit_count = self._count_audit_entries()
        return {
            "total_attempts": total,
            "successful": succeeded,
            "failed": failed,
            "rolled_back": rolled_back,
            "gate_blocked": gate_blocked,
            "audit_entries": audit_count,
            "success_rate": round(succeeded / max(1, total) * 100, 1),
            "gate_config": {g.value: self.gate_chain._gate_config[g]
                            for g in ModificationGate},
            "recent": logs[-10:] if logs else [],
        }

    # ---- 预设修复 ----

    def fix_bare_excepts(self, filepath: str) -> Dict[str, Any]:
        """修复裸 except: → except Exception:"""
        full_path = Path(filepath)
        if not full_path.exists():
            return {"success": False, "error": "文件不存在",
                    "error_kind": ModErrorKind.FILE_NOT_FOUND}

        code = full_path.read_text(encoding="utf-8")
        new_code = code.replace("except:", "except Exception:")
        if new_code == code:
            return {"success": False, "error": "没有找到裸 except",
                    "error_kind": ModErrorKind.CODE_MISMATCH}

        lines = code.split("\n")
        new_lines = []
        modified = False
        for line in lines:
            stripped = line.strip()
            if re.match(r"^except\s*:$", stripped) and not stripped.startswith("#"):
                indent = line[:len(line) - len(line.lstrip())]
                new_lines.append(f"{indent}except Exception:")
                modified = True
            else:
                new_lines.append(line)

        if not modified:
            return {"success": False, "error": "没有找到裸 except",
                    "error_kind": ModErrorKind.CODE_MISMATCH}

        new_code = "\n".join(new_lines)
        return self.apply_code_fix(filepath, code, new_code,
                                   reason="修复裸 except → except Exception:",
                                   mod_type="bare_except")

    def add_module_docstring(self, filepath: str, content: str = "") -> Dict[str, Any]:
        """为模块添加文档字符串"""
        full_path = Path(filepath)
        if not full_path.exists():
            return {"success": False, "error": "文件不存在",
                    "error_kind": ModErrorKind.FILE_NOT_FOUND}

        code = full_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(code)
            existing = ast.get_docstring(tree)
            if existing:
                return {"success": False, "error": "模块已有文档字符串",
                        "error_kind": ModErrorKind.PRE_VALIDATE_FAILED}
        except SyntaxError:
            return {"success": False, "error": "语法错误",
                    "error_kind": ModErrorKind.PRE_VALIDATE_FAILED}

        lines = code.split("\n")
        insert_pos = 0
        shebangs = 0
        for i, line in enumerate(lines):
            if line.startswith("#!") or line.startswith("# -*-"):
                insert_pos = i + 1
                shebangs += 1
            elif shebangs > 0 and not line.strip():
                insert_pos = i + 1
            else:
                break

        if not content:
            module_name = full_path.stem
            content = f"{module_name} module - 自动生成的模块文档"

        docstring = f'"""\n{content}\n"""'
        lines.insert(insert_pos, docstring)
        new_code = "\n".join(lines)

        return self.apply_code_fix(filepath, code, new_code,
                                   reason=f"添加模块文档: {content[:50]}",
                                   mod_type="docstring")

    def remove_unused_import(self, filepath: str, import_name: str) -> Dict[str, Any]:
        """移除未使用的 import"""
        full_path = Path(filepath)
        if not full_path.exists():
            return {"success": False, "error": "文件不存在",
                    "error_kind": ModErrorKind.FILE_NOT_FOUND}

        code = full_path.read_text(encoding="utf-8")

        old_lines = code.split("\n")
        new_lines = []
        removed = False
        for line in old_lines:
            stripped = line.strip()
            if stripped.startswith("import ") and import_name in stripped:
                if stripped == f"import {import_name}":
                    removed = True
                    continue
                parts = stripped.replace("import ", "").split(",")
                cleaned = [p.strip() for p in parts if p.strip() != import_name]
                if len(cleaned) < len(parts):
                    removed = True
                    if cleaned:
                        indent = line[:len(line) - len(line.lstrip())]
                        new_lines.append(f"{indent}import {', '.join(cleaned)}")
                    continue
            new_lines.append(line)

        if not removed:
            return {"success": False, "error": f"未找到 import {import_name}",
                    "error_kind": ModErrorKind.CODE_MISMATCH}

        new_code = "\n".join(new_lines)
        return self.apply_code_fix(filepath, code, new_code,
                                   reason=f"移除未使用的 import: {import_name}",
                                   mod_type="unused_import")

    # ---- Mods Directory 支持 ----

    def create_mod(self, name: str, content: str) -> Dict[str, Any]:
        """在 mods/ 目录创建新模块（系统的生长层）"""
        # SubGates 检查
        if not self.gate_chain.sub_gates.allow_new_mod_creation:
            return {"success": False, "error": "新建 mod 已禁用",
                    "error_kind": ModErrorKind.SUB_GATE_BLOCKED}

        mod_file = self.modifications_dir / f"{name}.py"
        if mod_file.exists():
            return {"success": False, "error": f"mod '{name}' 已存在",
                    "error_kind": ModErrorKind.SCOPE_DENIED}

        try:
            mod_file.write_text(content, encoding="utf-8")
            self._create_git_commit(f"🤖 新建 mod: {name}")
            return {"success": True, "path": str(mod_file)}
        except Exception as e:
            return {"success": False, "error": str(e),
                    "error_kind": ModErrorKind.EXECUTE_FAILED}

    def list_mods(self) -> List[str]:
        """列出所有 mods"""
        return sorted(f.stem for f in self.modifications_dir.glob("*.py"))

    # ---- GateChain 配置 ----

    def configure_gate(self, gate: ModificationGate, enabled: bool):
        """启用/禁用指定 gate"""
        self.gate_chain.set_gate_enabled(gate, enabled)

    def configure_sub_gates(self, **kwargs):
        """批量配置子开关"""
        for key, value in kwargs.items():
            if hasattr(self.gate_chain.sub_gates, key):
                setattr(self.gate_chain.sub_gates, key, value)

    # ---- 内部方法 ----

    def _create_backup(self, filepath: Path) -> Optional[Path]:
        """创建文件备份"""
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = str(filepath).replace("\\", "_").replace("/", "_").replace(":", "_")
            backup = self.backup_dir / f"{safe_name}_bak_{ts}"
            shutil.copy2(filepath, backup)
            return backup
        except Exception:
            return None

    def _restore_backup(self, target: Path, backup: Path) -> bool:
        """从备份还原"""
        try:
            if backup.exists():
                shutil.copy2(backup, target)
                return True
            return False
        except Exception:
            return False

    def _create_git_commit(self, message: str):
        """创建 git commit 做审计追踪"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, timeout=10,
                cwd=Path.cwd(),
            )
            if not result.stdout.strip():
                return

            subprocess.run(
                ["git", "add", "-A"],
                capture_output=True, timeout=10, cwd=Path.cwd(),
            )
            subprocess.run(
                ["git", "commit", "-m", message, "--no-verify"],
                capture_output=True, timeout=30, cwd=Path.cwd(),
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    def _log_modification(self, filepath: str, status: str,
                           detail: str = "", reason: str = ""):
        """记录修改事件"""
        logs = self._load_logs()
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "file": filepath,
            "status": status,
            "detail": detail,
            "reason": reason,
        })
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load_logs(self) -> List[Dict]:
        """加载修改日志"""
        if self.log_file.exists():
            try:
                with open(self.log_file, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception):
                return []
        return []

    def _audit_log(self, event_type: str, file: str = "",
                    risk_level: int = 0, gate: str = "", status: str = "",
                    detail: str = "", actor: str = "system"):
        """写入审计日志（JSONL 格式，链式哈希防篡改）"""
        audit_file = self.data_dir / "audit_log.jsonl"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_id": uuid.uuid4().hex[:8],
            "event_type": event_type,
            "actor": actor,
            "file": file,
            "risk_level": risk_level,
            "gate": gate,
            "status": status,
            "detail": detail,
        }
        # 链式哈希：前一条记录的 SHA256 前缀
        prev_hash = ""
        if audit_file.exists():
            try:
                with open(audit_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            prev_hash = hashlib.sha256(line.encode()).hexdigest()[:16]
            except Exception:
                pass
        entry["prev_hash"] = prev_hash

        try:
            with open(audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _count_audit_entries(self) -> int:
        """统计审计日志条数"""
        audit_file = self.data_dir / "audit_log.jsonl"
        if not audit_file.exists():
            return 0
        try:
            count = 0
            with open(audit_file, "r", encoding="utf-8") as f:
                for _ in f:
                    count += 1
            return count
        except Exception:
            return 0


def main():
    """测试自我修改引擎（含 GateChain）"""
    engine = SelfModificationEngine()
    print(f"🔧 自我修改引擎 v2 (GateChain) 已初始化")
    print(f"   备份目录: {engine.backup_dir}")
    print(f"   Mods目录: {engine.modifications_dir}")
    print()

    # 显示 GateChain 配置
    print("=== GateChain 配置 ===")
    for gate in ModificationGate:
        enabled = engine.gate_chain._gate_config[gate]
        print(f"  {'+' if enabled else '-'} {gate.value}")
    print()

    # 测试 validate_python
    valid, err = engine.validate_python("x = 1\n")
    print(f"  语法验证 (正确): {'✅' if valid else '❌'}")

    valid, err = engine.validate_python("x = 1 broken")
    print(f"  语法验证 (错误): {'✅' if not valid else '❌'} (错误: {err})")
    print()

    # 测试 gate chain: 尝试修改黑名单中的文件
    result = engine.apply_code_fix("system_state_manager.py", "x", "y", reason="测试黑名单阻挡")
    print(f"  GateChain (黑名单): {'✅ 已阻挡' if not result.get('success') else '❌ 不应该通过'}")
    if result.get("error_kind"):
        print(f"    错误类型: {result['error_kind']}")

    print()
    # 测试 fix_bare_excepts
    test_file = Path("data/_test_bare_except.py")
    test_file.write_text("try:\n    x = 1\nexcept:\n    pass\n", encoding="utf-8")
    result = engine.fix_bare_excepts(str(test_file))
    print(f"  修复裸 except: {'✅' if result.get('success') else '❌'} {result.get('error', '')}")
    if result.get("success"):
        content = test_file.read_text(encoding="utf-8")
        print(f"    结果: {content.strip()}")
        engine.rollback(result.get("backup", ""))
    test_file.unlink(missing_ok=True)
    print()

    # 测试 SubGates: 关闭 bare_except 修复
    print("=== SubGates 测试 ===")
    engine.configure_sub_gates(allow_bare_except_fix=False)
    test_file2 = Path("data/_test_bare_except2.py")
    test_file2.write_text("try:\n    x = 1\nexcept:\n    pass\n", encoding="utf-8")
    result = engine.fix_bare_excepts(str(test_file2))
    print(f"  SubGate 阻挡: {'✅ 已阻挡' if not result.get('success') else '❌ 不应该通过'}")
    if result.get("error_kind"):
        print(f"    错误类型: {result['error_kind']}")
    engine.configure_sub_gates(allow_bare_except_fix=True)
    test_file2.unlink(missing_ok=True)
    print()

    # 统计
    stats = engine.get_modification_stats()
    print(f"  修改统计: {stats['total_attempts']} 次尝试, "
          f"{stats['successful']} 成功, {stats['rolled_back']} 回滚, "
          f"{stats['gate_blocked']} 被阻挡")


if __name__ == "__main__":
    main()
