#!/usr/bin/env python3
"""
🔧 自我修改引擎 — 安全地修改自身代码
基于 Mods Directory + Git Versioning 模式
每个修改都有备份、验证、审计追踪
"""

import ast
import json
import os
import shutil
import subprocess
import tempfile
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class SelfModificationEngine:
    """安全的自我修改引擎"""

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.log_file = self.data_dir / "modification_log.json"
        self.backup_dir = self.data_dir / "mod_backups"
        self.backup_dir.mkdir(exist_ok=True)
        self.modifications_dir = Path("mods")
        self.modifications_dir.mkdir(exist_ok=True)

    # ---- 核心操作 ----

    def apply_code_fix(self, filepath: str, old_code: str, new_code: str,
                       reason: str = "") -> Dict[str, Any]:
        """原子级代码修复：备份 → 写入 → 验证 → 提交"""
        full_path = Path(filepath).resolve()
        if not full_path.exists():
            return {"success": False, "error": f"文件不存在: {filepath}"}

        # 1. 创建备份
        backup_path = self._create_backup(full_path)
        if not backup_path:
            return {"success": False, "error": "备份失败"}

        # 2. 读取当前内容
        current = full_path.read_text(encoding="utf-8")
        if old_code not in current:
            self._log_modification(filepath, "failed", reason, "old_code_not_found")
            return {"success": False, "error": "代码匹配失败，可能文件已被修改"}

        # 3. 写入新代码
        new_content = current.replace(old_code, new_code, 1)
        try:
            full_path.write_text(new_content, encoding="utf-8")
        except Exception as e:
            self._restore_backup(full_path, backup_path)
            return {"success": False, "error": f"写入失败: {e}"}

        # 4. 语法验证
        valid, error = self.validate_python(new_content)
        if not valid:
            self._restore_backup(full_path, backup_path)
            self._log_modification(filepath, "rolled_back", f"语法错误: {error}", reason)
            return {"success": False, "error": f"语法验证失败: {error}"}

        # 5. 创建 git commit（审计追踪）
        commit_msg = f"🤖 自我修改: {reason or filepath}"
        self._create_git_commit(commit_msg)

        # 6. 记录成功
        self._log_modification(filepath, "success", reason,
                               f"修改成功 → git commit: {commit_msg}")
        return {"success": True, "backup": str(backup_path)}

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
        # 从备份名推断原文件路径
        original_name = backup.name.replace(".bak_", ".")
        # 在 backup_dir 的同级找原文件
        for f in self.backup_dir.iterdir():
            if f.name == backup.name:
                continue
        # 尝试在项目根找
        original = Path(original_name)
        if not original.exists():
            # 可能原路径在备份文件名编码中
            stem = backup.stem  # e.g. "self_thinking_agent.py_bak_xxx"
            base = stem.split("_bak_")[0]
            candidate = Path(base)
            if candidate.exists():
                original = candidate

        return self._restore_backup(original, backup)

    def get_modification_stats(self) -> Dict[str, Any]:
        """获取修改统计"""
        logs = self._load_logs()
        total = len(logs)
        succeeded = sum(1 for l in logs if l.get("status") == "success")
        failed = sum(1 for l in logs if l.get("status") == "failed")
        rolled_back = sum(1 for l in logs if l.get("status") == "rolled_back")
        return {
            "total_attempts": total,
            "successful": succeeded,
            "failed": failed,
            "rolled_back": rolled_back,
            "success_rate": round(succeeded / max(1, total) * 100, 1),
            "recent": logs[-10:] if logs else [],
        }

    # ---- 预设修复 ----

    def fix_bare_excepts(self, filepath: str) -> Dict[str, Any]:
        """修复裸 except: → except Exception:"""
        full_path = Path(filepath)
        if not full_path.exists():
            return {"success": False, "error": "文件不存在"}

        code = full_path.read_text(encoding="utf-8")
        new_code = code.replace("except:", "except Exception:")
        if new_code == code:
            return {"success": False, "error": "没有找到裸 except"}

        # 逐行检查，只替换真正的裸 except（不是注释或字符串里的）
        import re
        lines = code.split("\n")
        new_lines = []
        modified = False
        for line in lines:
            stripped = line.strip()
            # 匹配 exc ept: 但排除注释和字符串中的
            if re.match(r"^except\s*:$", stripped) and not stripped.startswith("#"):
                indent = line[:len(line) - len(line.lstrip())]
                new_lines.append(f"{indent}except Exception:")
                modified = True
            else:
                new_lines.append(line)

        if not modified:
            return {"success": False, "error": "没有找到裸 except"}

        new_code = "\n".join(new_lines)
        return self.apply_code_fix(filepath, code, new_code,
                                    reason="修复裸 except → except Exception:")

    def add_module_docstring(self, filepath: str, content: str = "") -> Dict[str, Any]:
        """为模块添加文档字符串"""
        full_path = Path(filepath)
        if not full_path.exists():
            return {"success": False, "error": "文件不存在"}

        code = full_path.read_text(encoding="utf-8")
        # 检查是否已有 docstring
        try:
            tree = ast.parse(code)
            existing = ast.get_docstring(tree)
            if existing:
                return {"success": False, "error": "模块已有文档字符串"}
        except SyntaxError:
            return {"success": False, "error": "语法错误"}

        # 在文件头部（shebang 和编码声明之后）插入文档字符串
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
                                    reason=f"添加模块文档: {content[:50]}")

    def remove_unused_import(self, filepath: str, import_name: str) -> Dict[str, Any]:
        """移除未使用的 import"""
        full_path = Path(filepath)
        if not full_path.exists():
            return {"success": False, "error": "文件不存在"}

        code = full_path.read_text(encoding="utf-8")

        # 只移除显式指定的 import 语句
        old_lines = code.split("\n")
        new_lines = []
        removed = False
        for line in old_lines:
            stripped = line.strip()
            if stripped.startswith("import ") and import_name in stripped:
                # 检查是否整个行就是 import X
                if stripped == f"import {import_name}":
                    removed = True
                    continue
                # 检查是否 import A, B, C 中的一部分
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
            return {"success": False, "error": f"未找到 import {import_name}"}

        new_code = "\n".join(new_lines)
        return self.apply_code_fix(filepath, code, new_code,
                                    reason=f"移除未使用的 import: {import_name}")

    # ---- Mods Directory 支持 ----

    def create_mod(self, name: str, content: str) -> Dict[str, Any]:
        """在 mods/ 目录创建新模块（系统的"生长层"）"""
        mod_file = self.modifications_dir / f"{name}.py"
        if mod_file.exists():
            return {"success": False, "error": f"mod '{name}' 已存在"}

        try:
            mod_file.write_text(content, encoding="utf-8")
            self._create_git_commit(f"🤖 新建 mod: {name}")
            return {"success": True, "path": str(mod_file)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_mods(self) -> List[str]:
        """列出所有 mods"""
        return sorted(f.stem for f in self.modifications_dir.glob("*.py"))

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
            # 只在 git 仓库中执行
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, timeout=10,
                cwd=Path.cwd(),
            )
            if not result.stdout.strip():
                return  # 没有变更，不提交空 commit

            subprocess.run(
                ["git", "add", "-A"],
                capture_output=True, timeout=10, cwd=Path.cwd(),
            )
            subprocess.run(
                ["git", "commit", "-m", message, "--no-verify"],
                capture_output=True, timeout=30, cwd=Path.cwd(),
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass  # 不是 git 仓库或 git 不可用

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


def main():
    """测试自我修改引擎"""
    engine = SelfModificationEngine()
    print(f"🔧 自我修改引擎已初始化")
    print(f"   备份目录: {engine.backup_dir}")
    print(f"   Mods目录: {engine.modifications_dir}")
    print()

    # 测试 validate_python
    valid, err = engine.validate_python("x = 1\n")
    print(f"  语法验证 (正确): {'✅' if valid else '❌'}")

    valid, err = engine.validate_python("x = 1 broken")
    print(f"  语法验证 (错误): {'✅' if not valid else '❌'} (错误: {err})")

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

    # 统计
    stats = engine.get_modification_stats()
    print(f"\n  修改统计: {stats['total_attempts']} 次尝试, "
          f"{stats['successful']} 成功, {stats['rolled_back']} 回滚")


if __name__ == "__main__":
    main()
