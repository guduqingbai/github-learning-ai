#!/usr/bin/env python3
"""
⚖️ 宪法 Gate — 宪法规则的运行时检查

从 constitution.py 读取硬编码常量，执行修改请求的宪法合规检查。
独立于 GateChain config，始终启用，不可绕过。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set

from constitution import (
    CONSTITUTION_MODULES,
    CONSTITUTION_KEYWORDS,
    verify_integrity,
    store_checksums,
)

# 重新导出，方便外部只 import constitution_gate
__all__ = [
    "ConstitutionalPrinciple",
    "ConstitutionCheckResult",
    "check_modification",
    "is_constitutional_file",
    "verify_integrity",
    "store_checksums",
]


@dataclass
class ConstitutionalPrinciple:
    """一条宪法原则"""
    name: str
    description: str
    severity: str = "fundamental"


@dataclass
class ConstitutionCheckResult:
    """宪法检查结果"""
    passed: bool
    violated_principles: List[str] = field(default_factory=list)
    suggested_action: str = ""


def check_modification(
    filepath: str, new_code: str, reason: str = ""
) -> ConstitutionCheckResult:
    """
    检查一个修改请求是否符合宪法。

    检查项：
    - CON.2: 文件是否在不可修改列表中
    - CON.5: 修改内容是否包含安全机制关键词
    """
    fname = Path(filepath).name
    violated: List[str] = []

    # CON.2: 不可修改文件
    if fname in CONSTITUTION_MODULES:
        violated.append(f"第二条：{fname} 受宪法保护，禁止修改")

    # CON.2 别名匹配（path 级）
    for protected in CONSTITUTION_MODULES:
        if filepath.endswith(protected):
            violated.append(
                f"第二条（别名匹配）：{filepath} 受宪法保护，禁止修改"
            )
            break

    # CON.5: 试图削弱安全机制
    if fname not in CONSTITUTION_MODULES:
        for kw in CONSTITUTION_KEYWORDS:
            if kw in new_code:
                violated.append(
                    f"第五条：修改内容包含安全关键词 '{kw}'，疑似削弱安全机制"
                )
                break

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
    if fname in CONSTITUTION_MODULES:
        return True
    for protected in CONSTITUTION_MODULES:
        if path.endswith(protected):
            return True
    return False


def main():
    """测试宪法 Gate"""
    print("=" * 50)
    print("  ConstitutionGate 测试")
    print("=" * 50)

    # 1. 宪法文件保护测试
    print("\n1. 宪法文件保护测试")
    for mod in CONSTITUTION_MODULES:
        result = check_modification(mod, "# 恶意修改代码")
        status = "✅ 拦截" if not result.passed else "❌ 漏过"
        detail = ""
        if result.violated_principles:
            detail = result.violated_principles[0][:40] + "..."
        print(f"   {mod}: {status} {detail}")

    # 2. 安全关键词检测
    print("\n2. 安全关键词检测")
    result = check_modification("some_file.py", "DENIED_SCOPE = []  # 清空黑名单")
    assert not result.passed
    print("   security keyword: ✅ 拦截")

    # 3. 允许的正常修改
    print("\n3. 正常修改放过")
    result = check_modification("curiosity_engine.py", "print('hello')", "正常功能修改")
    assert result.passed
    print("   curiosity_engine.py: ✅ 通过")

    # 4. is_constitutional_file
    print("\n4. 受保护文件判断")
    assert is_constitutional_file("constitution.py")
    assert is_constitutional_file("CONSTITUTION.md")
    assert is_constitutional_file("data/../CONSTITUTION.md")
    assert not is_constitutional_file("curiosity_engine.py")
    print("   ✅ is_constitutional_file 逻辑正常")

    # 5. 完整性校验（实委托给 constitution.py）
    print("\n5. 完整性校验")
    ok = verify_integrity()
    print(f"   校验结果: {'✅ 通过' if ok else '❌ 失败'}")

    print("\n✅ 宪法 Gate 测试完成")
    return True


if __name__ == "__main__":
    main()
