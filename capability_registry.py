#!/usr/bin/env python3
"""
📋 能力注册表 — 结构化、持久化、可版本化的能力清单

替代 self_thinking_agent.py 中硬编码的 11 条能力列表，
支持自动发现、依赖追踪和版本历史。
"""
import ast
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


@dataclass
class Capability:
    """一项能力——系统知道自己能做什么"""
    name: str                           # 如 "代码扫描"
    module: str                         # 如 "self_scanner.py"
    enabled: bool = True
    version: str = "1.0.0"             # 语义化版本
    description: str = ""               # 能力描述
    dependencies: List[str] = field(default_factory=list)  # 依赖的其他能力名
    confidence: float = 0.5            # 0-1 该能力当前可靠度
    last_verified: str = ""             # ISO 时间


class CapabilityRegistry:
    """
    能力注册表——持久化管理系统的全部已知能力。

    职责：
    1. 维护能力列表（CRUD）
    2. 自动扫描 .py 文件发现新能力
    3. 追踪能力版本变更历史
    4. 替代硬编码能力列表
    """

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

        self._registry_file = self.data_dir / "capability_registry.json"
        self._history_file = self.data_dir / "capability_registry_history.json"

        # name -> Capability
        self._capabilities: Dict[str, Capability] = {}

        # 版本历史: name -> list of {timestamp, old_version, new_version}
        self._version_history: Dict[str, List[Dict]] = {}

        self._load()

    # ── CRUD ──

    def register(self, capability: Capability) -> bool:
        """
        注册一项能力。如果同名已存在且版本相同则跳过。
        返回 True 表示实际注册了变更。
        """
        existing = self._capabilities.get(capability.name)
        if existing and existing.version == capability.version:
            return False

        old_version = existing.version if existing else None
        self._capabilities[capability.name] = capability

        if old_version and old_version != capability.version:
            self._track_version(capability.name, old_version, capability.version)

        self._save()
        return True

    def unregister(self, name: str) -> bool:
        """注销一项能力。不存在则返回 False。"""
        if name not in self._capabilities:
            return False
        del self._capabilities[name]
        self._save()
        return True

    def get(self, name: str) -> Optional[Capability]:
        """按名称查找能力。"""
        return self._capabilities.get(name)

    def list(self) -> List[Capability]:
        """返回全部已注册能力（副本）。"""
        return list(self._capabilities.values())

    def to_serializable_list(self) -> List[Dict[str, Any]]:
        """返回可序列化的能力列表（用于自我认知 JSON）。"""
        return [
            {
                "name": c.name,
                "module": c.module,
                "enabled": c.enabled,
                "version": c.version,
                "description": c.description,
                "confidence": c.confidence,
                "last_verified": c.last_verified,
                "dependencies": list(c.dependencies),
            }
            for c in self._capabilities.values()
        ]

    # ── 自动发现 ──

    def auto_discover(self) -> List[Capability]:
        """
        扫描项目根目录所有 .py 文件，查找模块级变量 __capability__。
        如果找到一个 dict {name, module, description, ...}，自动注册。
        返回新发现的能力列表。
        """
        discovered = []
        for py_file in Path(".").glob("*.py"):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if (isinstance(target, ast.Name)
                                    and target.id == "__capability__"
                                    and isinstance(node.value, ast.Dict)):
                                cap = self._parse_capability_ast(node.value, py_file.name)
                                if cap:
                                    if self.register(cap):
                                        discovered.append(cap)
            except Exception:
                continue
        return discovered

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """返回能力依赖关系图 {能力名: [依赖的能力名]}"""
        return {c.name: list(c.dependencies) for c in self._capabilities.values()}

    def get_version_history(self, name: str) -> List[Dict]:
        """返回指定能力的版本历史"""
        return list(self._version_history.get(name, []))

    # ── 内部 ──

    def _parse_capability_ast(self, dct: ast.Dict, module: str) -> Optional[Capability]:
        """从 AST Dict 节点解析 Capability"""
        fields = {}
        for key_node, value_node in zip(dct.keys, dct.values):
            if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                key = key_node.value
                if isinstance(value_node, ast.Constant):
                    fields[key] = value_node.value
                elif isinstance(value_node, ast.List):
                    fields[key] = [
                        e.value for e in value_node.elts
                        if isinstance(e, ast.Constant)
                    ]
        if "name" not in fields:
            return None
        return Capability(
            name=str(fields.get("name", "")),
            module=str(fields.get("module", module)),
            enabled=bool(fields.get("enabled", True)),
            version=str(fields.get("version", "1.0.0")),
            description=str(fields.get("description", "")),
            dependencies=fields.get("dependencies", []),
        )

    def _track_version(self, name: str, old_ver: str, new_ver: str):
        """记录版本变更"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "capability": name,
            "old_version": old_ver,
            "new_version": new_ver,
        }
        self._version_history.setdefault(name, []).append(entry)
        try:
            history = []
            if self._history_file.exists():
                history = json.loads(self._history_file.read_text(encoding="utf-8"))
            history.append(entry)
            self._history_file.write_text(
                json.dumps(history[-200:], ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass

    def _load(self):
        """从文件加载注册表"""
        if not self._registry_file.exists():
            for cap in self._get_default_capabilities():
                self._capabilities[cap.name] = cap
            self._save()
            return
        try:
            data = json.loads(self._registry_file.read_text(encoding="utf-8"))
            entries = data if isinstance(data, list) else data.get("capabilities", [])
            for item in entries:
                cap = Capability(
                    name=item.get("name", "未知"),
                    module=item.get("module", ""),
                    enabled=item.get("enabled", True),
                    version=item.get("version", "1.0.0"),
                    description=item.get("description", ""),
                    dependencies=item.get("dependencies", []),
                    confidence=item.get("confidence", 0.5),
                    last_verified=item.get("last_verified", ""),
                )
                self._capabilities[cap.name] = cap
        except Exception:
            pass

        # 如果加载后为空（空文件或损坏），用默认值填充
        if not self._capabilities:
            for cap in self._get_default_capabilities():
                self._capabilities[cap.name] = cap
            self._save()

    def _save(self):
        """持久化到文件"""
        try:
            data = {
                "capabilities": self.to_serializable_list(),
                "updated_at": datetime.now().isoformat(),
            }
            self._registry_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass

    @staticmethod
    def _get_default_capabilities() -> List[Capability]:
        """返回出厂默认的 11 条能力（与现有硬编码列表一致）"""
        return [
            Capability("代码扫描", "self_scanner.py",
                       description="扫描项目文件结构、代码质量、依赖关系"),
            Capability("好奇心提问", "curiosity_engine.py",
                       description="基于扫描数据生成好奇心问题"),
            Capability("自我修改", "self_modification_engine.py",
                       description="安全地修改自身代码"),
            Capability("知识学习", "knowledge_base.py",
                       description="知识库管理与学习"),
            Capability("网络爬虫", "ai_knowledge_crawler.py",
                       description="定时爬取网络知识"),
            Capability("浏览器操控", "hands_engine.py",
                       description="自动化浏览器操作"),
            Capability("内容生产", "content_studio.py",
                       description="生成内容输出"),
            Capability("市场监控", "trading_bot.py",
                       description="监控市场数据"),
            Capability("后台守护", "thinking_daemon.py",
                       description="后台守护进程运行"),
            Capability("自我评估", "self_thinking_agent.py",
                       description="自我评估与画像构建"),
            Capability("目标追踪", "self_thinking_agent.py",
                       description="设定和追踪改进目标"),
        ]


def main():
    """测试 CapabilityRegistry"""
    print("=" * 50)
    print("  CapabilityRegistry 测试")
    print("=" * 50)

    reg = CapabilityRegistry()
    caps = reg.list()
    print(f"\n1. 默认能力数: {len(caps)}")
    for c in caps:
        print(f"   [{c.name}] {c.module}  v{c.version}")

    print(f"\n2. 自动发现 __capability__ 变量...")
    discovered = reg.auto_discover()
    print(f"   新发现: {len(discovered)} 项")

    print(f"\n3. 注册新能力...")
    new_cap = Capability("测试能力", "test.py",
                          description="注册测试",
                          version="0.1.0",
                          dependencies=["代码扫描"])
    ok = reg.register(new_cap)
    print(f"   注册结果: {ok}")
    assert ok, "注册应成功"

    # 再次注册相同版本应跳过
    ok2 = reg.register(new_cap)
    assert not ok2, "重复注册应跳过"

    # 获取测试
    fetched = reg.get("测试能力")
    assert fetched is not None, "应能获取刚注册的能力"
    assert fetched.name == "测试能力"

    # 依赖图
    graph = reg.get_dependency_graph()
    print(f"   依赖图条目数: {len(graph)}")

    # 注销
    reg.unregister("测试能力")
    assert reg.get("测试能力") is None, "注销后应不存在"

    print("\n✅ CapabilityRegistry 测试完成")
    return True


if __name__ == "__main__":
    main()
