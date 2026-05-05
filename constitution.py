#!/usr/bin/env python3
"""
⚖️ 宪法核心 — 硬编码的不可修改规则（系统最高约束）

这是整个系统的最高行为准则层。与 CONSTITUTION.md（人类可读版）同步。
所有安全机制（constitution_gate.py、DENIED_SCOPE 等）从此处读取数据。

防护链：
  constitution.py (本文件) ← constitution_gate.py ← GateChain ← OS 文件权限
    硬编码常量       运行时检查        执行时拦截      chmod -w
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List

# ═══════════════════════════════════════════════════
# 第一条：不可变更的硬编码规则
# ═══════════════════════════════════════════════════
# 警告：任何修改此列表的尝试将被系统硬拒绝。
# 如需修改，主人必须手动编辑此文件并重新计算校验和。
IMMUTABLE_RULES: List[str] = [
    "以主人指令为最终权威",
    "不得修改本文件",                   # constitution.py 自身
    "不得删除或绕过主人的控制接口",       # feature flags, kill switch 等
    "不得在未经确认的情况下执行破坏性操作",
    "不得删除或修改宪法保护的文件列表",
    "每次修改后必须验证宪法完整性",
]

# ═══════════════════════════════════════════════════
# 第二条：宪法保护的模块
# ═══════════════════════════════════════════════════
# 此列表中的文件受宪法 Gate 保护，任何修改被硬拒绝。
# 同步更新：修改此列表后必须同步更新：
#   - self_modification_engine.py 中的 DENIED_SCOPE
#   - OS 文件权限（建议 chmod -w）
CONSTITUTION_MODULES: List[str] = [
    "constitution.py",
    "constitution_gate.py",
    "CONSTITUTION.md",
    "self_modification_engine.py",
    "knowledge_base.py",
    "system_state_manager.py",
    "thought_continuity.py",
    "start_thinking.py",
]

# ═══════════════════════════════════════════════════
# 第五条：安全关键词（出现在修改内容中时触发拦截）
# ═══════════════════════════════════════════════════
# 任何修改尝试如果包含以下关键词之一，将被宪法 Gate 拦截。
CONSTITUTION_KEYWORDS: List[str] = [
    # 宪法核心
    "IMMUTABLE_RULES",
    "CONSTITUTION_MODULES",
    "CONSTITUTION_KEYWORDS",
    "constitution_protection",
    "CONSTITUTION_VIOLATION",
    # 安全机制
    "KILL_SWITCH",
    "DENIED_SCOPE",
    "GateChain",
    "ModificationGate",
    "ModErrorKind",
    # 门禁函数
    "_gate_constitution",
    "check_modification",
    "verify_integrity",
    "is_constitutional_file",
    # 旧版（兼容）
    "CONSTITUTIONAL_FILES",
    "SECURITY_KEYWORDS",
]

# ═══════════════════════════════════════════════════
# 完整性校验（SHA-256）
# ═══════════════════════════════════════════════════

_CHECKSUM_FILE = Path("data") / "constitution_checksum.json"


def _sha256(filepath: Path) -> str:
    """计算文件的 SHA-256 哈希"""
    h = hashlib.sha256()
    h.update(filepath.read_bytes())
    return h.hexdigest()


def store_checksums():
    """计算并存储所有宪法模块的 SHA-256 校验和"""
    checksums = {}
    for mod in CONSTITUTION_MODULES:
        p = Path(mod)
        if p.exists():
            checksums[mod] = _sha256(p)
    data = {
        "checksums": checksums,
        "updated_at": datetime.now().isoformat(),
        "immutable_rules_count": len(IMMUTABLE_RULES),
        "constitution_modules_count": len(CONSTITUTION_MODULES),
    }
    _CHECKSUM_FILE.parent.mkdir(exist_ok=True)
    _CHECKSUM_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def verify_integrity() -> bool:
    """
    校验所有宪法模块的 SHA-256 完整性。

    返回 True = 完整，False = 被篡改。
    启动时和每次自我修改后调用。
    """
    if not _CHECKSUM_FILE.exists():
        store_checksums()
        return True

    try:
        data = json.loads(_CHECKSUM_FILE.read_text(encoding="utf-8"))
        stored = data.get("checksums", {})
        all_ok = True

        for mod in CONSTITUTION_MODULES:
            p = Path(mod)
            if not p.exists():
                print(f"  ❌ 宪法模块缺失: {mod}")
                all_ok = False
                continue
            current = _sha256(p)
            expected = stored.get(mod)
            if expected is None:
                print(f"  ⚠️ {mod} 无校验记录，重新存储")
                all_ok = False
                continue
            if current != expected:
                print(f"  ❌ 宪法模块被篡改: {mod}")
                all_ok = False

        return all_ok

    except Exception as e:
        print(f"  ❌ 完整性校验异常: {e}")
        return False


# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 50)
    print("  宪法核心 — 完整性测试")
    print("=" * 50)

    # 存储校验和
    store_checksums()
    ok = verify_integrity()
    print(f"\n  完整性校验: {'✅ 通过' if ok else '❌ 失败'}")

    # 显示规则
    print(f"\n  Ⅰ 不可变更规则 ({len(IMMUTABLE_RULES)} 条):")
    for i, r in enumerate(IMMUTABLE_RULES, 1):
        print(f"    {i}. {r}")

    # 显示受保护模块
    print(f"\n  Ⅱ 宪法保护模块 ({len(CONSTITUTION_MODULES)} 个):")
    for m in CONSTITUTION_MODULES:
        p = Path(m)
        exists = "✓" if p.exists() else "✗"
        print(f"    [{exists}] {m}")

    # 显示安全关键词数量
    print(
        f"\n  Ⅴ 安全关键词: {len(CONSTITUTION_KEYWORDS)} 个"
    )

    print(f"\n✅ 宪法核心就绪")
