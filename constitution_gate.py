#!/usr/bin/env python3
"""
⚖️ 宪法 Gate — 系统不可逾越的红线

GateChain 中的第二个 gate（接 KILL_SWITCH 之后）。
独立于 GateChain config，始终启用，不可绕过。
"""
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

# ── 宪法保护的文件列表 ──
# 与 CONSTITUTION.md 第二条同步。
# 这是运行时检查的依据，源文件是 CONSTITUTION.md。
CONSTITUTIONAL_FILES: Set[str] = {
    "CONSTITUTION.md",
    "constitution_gate.py",
    "self_modification_engine.py",
    "knowledge_base.py",
    "system_state_manager.py",
    "thought_continuity.py",
}

# 安全机制关键词——出现在修改内容中时触发拦截
SECURITY_KEYWORDS: List[str] = [
    "DENIED_SCOPE",
    "ALLOWED_SCOPE",
    "GateChain",
    "gate_chain",
    "CONSTITUTION",
    "constitution_gate",
    "KILL_SWITCH",
    "ModificationGate",
    "CONSTITUTIONAL_FILES",
    "SECURITY_KEYWORDS",
    "_gate_constitution",
    "constitution_protection",
]


@dataclass
class ConstitutionalPrinciple:
    """一条宪法原则"""
    name: str                # 如 "第二条：不可修改文件"
    description: str         # 原则说明
    severity: str = "fundamental"  # fundamental | important | guideline


@dataclass
class ConstitutionCheckResult:
    """宪法检查结果"""
    passed: bool
    violated_principles: List[str] = field(default_factory=list)
    suggested_action: str = ""  # block | warn | log


# ── SHA-256 完整性校验 ──

_INTEGRITY_FILE = Path("data") / "constitution_checksum.json"


def _compute_sha256(filepath: Path) -> str:
    """计算文件的 SHA-256 哈希"""
    h = hashlib.sha256()
    h.update(filepath.read_bytes())
    return h.hexdigest()


# ── 检查入口 ──

def check_modification(filepath: str, new_code: str, reason: str = "") -> ConstitutionCheckResult:
    """
    检查一个修改请求是否符合宪法。

    Args:
        filepath: 目标文件路径
        new_code: 修改后的代码内容
        reason: 修改原因

    Returns:
        ConstitutionCheckResult
    """
    fname = Path(filepath).name
    violated = []

    # CON.2: 不可修改文件
    if fname in CONSTITUTIONAL_FILES:
        violated.append(f"第二条：{fname} 受宪法保护，禁止修改")

    # CON.2 别名检查（path 级）
    for protected in CONSTITUTIONAL_FILES:
        if filepath.endswith(protected):
            violated.append(f"第二条（别名匹配）：{filepath} 受宪法保护，禁止修改")
            break

    # CON.5: 试图削弱安全机制
    if fname not in CONSTITUTIONAL_FILES:
        for kw in SECURITY_KEYWORDS:
            if kw in new_code:
                violated.append(f"第五条：修改内容包含安全机制关键词 '{kw}'，疑似削弱安全机制")
                break  # 一条即拦截

    if violated:
        return ConstitutionCheckResult(
            passed=False,
            violated_principles=violated,
            suggested_action="block",
        )
    return ConstitutionCheckResult(passed=True)


def is_constitutional_file(path: str) -> bool:
    """快速判断一个文件是否受宪法保护"""
    fname = Path(path).name
    if fname in CONSTITUTIONAL_FILES:
        return True
    for protected in CONSTITUTIONAL_FILES:
        if path.endswith(protected):
            return True
    return False


# ── 完整性校验 ──

CONSTITUTION_FILES_TO_CHECK = [
    Path("CONSTITUTION.md"),
    Path("constitution_gate.py"),
]


def store_integrity_checksums():
    """计算并存储宪法文件的 SHA-256 校验和"""
    checksums = {}
    for f in CONSTITUTION_FILES_TO_CHECK:
        if f.exists():
            checksums[f.name] = _compute_sha256(f)
    data = {
        "checksums": checksums,
        "updated_at": datetime.now().isoformat(),
    }
    _INTEGRITY_FILE.parent.mkdir(exist_ok=True)
    _INTEGRITY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def verify_integrity() -> bool:
    """
    校验宪法文件的完整性。
    返回 True = 完整，False = 被篡改。
    """
    if not _INTEGRITY_FILE.exists():
        # 首次运行，存储当前校验和
        store_integrity_checksums()
        return True

    try:
        data = json.loads(_INTEGRITY_FILE.read_text(encoding="utf-8"))
        stored = data.get("checksums", {})
        for f in CONSTITUTION_FILES_TO_CHECK:
            if not f.exists():
                print(f"  ❌ 宪法文件缺失: {f.name}")
                return False
            current = _compute_sha256(f)
            expected = stored.get(f.name)
            if expected is None:
                print(f"  ⚠️ 未找到 {f.name} 的校验记录，重新存储")
                store_integrity_checksums()
                continue
            if current != expected:
                print(f"  ❌ 宪法文件被篡改: {f.name}")
                return False
        return True
    except Exception as e:
        print(f"  ❌ 完整性校验异常: {e}")
        return False


def main():
    """测试宪法 Gate"""
    print("=" * 50)
    print("  ConstitutionGate 测试")
    print("=" * 50)

    # 1. 完整性校验
    print("\n1. 完整性校验测试")
    store_integrity_checksums()
    ok = verify_integrity()
    print(f"   校验结果: {'✅ 通过' if ok else '❌ 失败'}")
    assert ok

    # 2. 宪法文件保护
    print("\n2. 宪法文件保护测试")
    for fname in ["CONSTITUTION.md", "constitution_gate.py", "self_modification_engine.py"]:
        result = check_modification(fname, "# 恶意修改代码")
        assert not result.passed, f"{fname} 应被拦截"
        print(f'   {fname}: ✅ 拦截 (violated: {result.violated_principles[0][:30]}...)')

    # 3. 安全关键词检测
    print("\n3. 安全关键词检测")
    result = check_modification("some_file.py", "DENIED_SCOPE = []  # 清空黑名单")
    assert not result.passed
    print(f'   security keyword: ✅ 拦截')

    # 4. 允许的正常修改
    print("\n4. 正常修改放过")
    result = check_modification("curiosity_engine.py", "print('hello')", "正常功能修改")
    assert result.passed
    print(f'   curiosity_engine.py: ✅ 通过')

    # 5. is_constitutional_file
    print("\n5. 受保护文件判断")
    assert is_constitutional_file("CONSTITUTION.md")
    assert is_constitutional_file("data/../CONSTITUTION.md")
    assert not is_constitutional_file("curiosity_engine.py")
    print(f'   ✅ is_constitutional_file 逻辑正常')

    print("\n✅ 宪法 Gate 测试完成")
    return True


if __name__ == "__main__":
    main()
