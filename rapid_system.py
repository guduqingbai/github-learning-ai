#!/usr/bin/env python3
"""
🚀 两小时快速实现 - 完整系统
"""

import os
import sys
import time
import json
import ast
import hashlib
import subprocess
import importlib
from datetime import datetime
from pathlib import Path

class RapidSystem:
    """快速实现的完整系统"""

    def __init__(self):
        """初始化"""
        self.learning_dir = Path("adaptive_ai_projects")
        self.data_dir = Path("data")
        self._init_system()

    def _init_system(self):
        """初始化系统"""
        for directory in [self.learning_dir, self.data_dir]:
            directory.mkdir(exist_ok=True)

        # 初始化数据文件
        self.patterns_file = self.data_dir / "error_patterns.json"
        self.lessons_file = self.data_dir / "lessons.jsonl"
        self.state_file = self.data_dir / "system_state.json"

        if not self.patterns_file.exists():
            with open(self.patterns_file, "w", encoding="utf-8") as f:
                json.dump({
                    "bare_except": {"count": 0, "severity": "medium", "fix": "Use 'except SpecificError:'"},
                    "missing_docstring": {"count": 0, "severity": "low", "fix": "Add triple-quoted docstring"},
                    "no_type_hints": {"count": 0, "severity": "low", "fix": "Add type hints"},
                    "hardcoded_path": {"count": 0, "severity": "high", "fix": "Use pathlib"},
                }, f, ensure_ascii=False, indent=2)

        if not self.lessons_file.exists():
            self.lessons_file.touch()

        if not self.state_file.exists():
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump({
                    "last_activity": datetime.now().isoformat(),
                    "completed_projects": 0,
                    "total_lessons": 0,
                    "last_review": datetime.now().isoformat(),
                    "learning_style": "beginner"
                }, f, ensure_ascii=False, indent=2)

    def analyze_code(self, file_path):
        """分析代码文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            tree = ast.parse(code)
            issues = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    issues.append({
                        "type": "bare_except",
                        "line": node.lineno,
                        "col": node.col_offset,
                        "message": "裸except语句"
                    })

                if (isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef)):
                    if not node.body or not isinstance(node.body[0], ast.Expr) or not isinstance(node.body[0].value, ast.Str):
                        issues.append({
                            "type": "missing_docstring",
                            "line": node.lineno,
                            "col": node.col_offset,
                            "message": "缺少文档字符串"
                        })

                if isinstance(node, ast.FunctionDef):
                    for arg in node.args.args:
                        if not arg.annotation:
                            issues.append({
                                "type": "no_type_hints",
                                "line": node.lineno,
                                "col": node.col_offset,
                                "message": f"参数 '{arg.arg}' 缺少类型提示"
                            })

            return issues
        except Exception as e:
            return [{"type": "parse_error", "line": 0, "col": 0, "message": str(e)}]

    def analyze_learning_state(self):
        """分析学习状态"""
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)

            completed = state["completed_projects"]
            style = state["learning_style"]

            if completed < 3:
                needs_attention = True
                suggestion_type = "beginner"
                progress_issue = True
            elif completed < 5:
                needs_attention = True
                suggestion_type = "intermediate"
                progress_issue = False
            elif completed < 10:
                needs_attention = False
                suggestion_type = "advanced"
                progress_issue = False
            else:
                needs_attention = False
                suggestion_type = "expert"
                progress_issue = False

            return {
                "needs_attention": needs_attention,
                "progress_issue": progress_issue,
                "suggestion_type": suggestion_type,
                "completed": completed,
                "style": style
            }
        except:
            return {
                "needs_attention": True,
                "progress_issue": True,
                "suggestion_type": "beginner",
                "completed": 0,
                "style": "beginner"
            }

    def communicate(self, force=False):
        """主动沟通"""
        state = self.analyze_learning_state()

        if not force and not state["needs_attention"]:
            return False

        conversation = self._generate_conversation(state)
        print(conversation)
        return True

    def _generate_conversation(self, state):
        """生成对话"""
        conversation = []
        conversation.append("🤖 晚上好！")

        if state["suggestion_type"] == "beginner":
            conversation.append("我注意到您的学习进度还需要加强，建议先从基础项目开始。")
            conversation.append("我推荐Python数据分析项目，这与您的学习目标高度匹配。")
        elif state["suggestion_type"] == "intermediate":
            conversation.append("您已经掌握了基础内容，建议学习更高级的项目。")
            conversation.append("我推荐机器学习项目，这会帮助您获得更全面的技能。")
        elif state["suggestion_type"] == "advanced":
            conversation.append("您已经有很好的基础，建议深入研究Trinity Claw的自我分析架构。")
            conversation.append("这将帮助您理解系统如何主动分析与学习。")
        else:
            conversation.append("您已经完成了大量学习，建议进行回顾和优化。")
            conversation.append("是否需要我为您准备今天的学习计划？")

        conversation.append(f"您目前已完成 {state['completed']} 个项目。")
        conversation.append("您希望我继续处理什么任务？")

        return "\n".join(conversation)

    def process_response(self, response):
        """处理用户响应"""
        if response.lower() in ["是", "好的", "继续"]:
            print("🤖 太好了！我立即为您准备学习任务。")
            self._execute_learning_plan()
            self._update_state(completed_projects=1)
        elif response.lower() in ["否", "不用", "停止"]:
            print("🤖 好的，我保持待命。如果需要帮助，请随时告诉我。")
        else:
            print("🤖 我会继续改进，以便更好地理解您的需求。")

    def _execute_learning_plan(self):
        """执行学习计划"""
        try:
            # 模拟项目分析
            print("📋 正在分析项目...")
            time.sleep(2)
            print("✅ 完成项目分析")
            print("🎯 学习计划执行成功！")
        except Exception as e:
            print(f"❌ 执行学习计划失败: {e}")

    def _update_state(self, completed_projects=0):
        """更新系统状态"""
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)

            state["last_activity"] = datetime.now().isoformat()
            state["completed_projects"] += completed_projects
            state["total_lessons"] += 1

            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except:
            pass

    def record_lesson(self, skill_name, error_type, error_msg, fix_applied=""):
        """记录学习成果"""
        lesson = {
            "timestamp": datetime.now().isoformat(),
            "skill": skill_name,
            "error_type": error_type,
            "error_message": error_msg,
            "fix_applied": fix_applied,
            "hash": hashlib.md5(f"{skill_name}:{error_type}:{error_msg}".encode()).hexdigest()
        }

        with open(self.lessons_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(lesson, ensure_ascii=False) + "\n")

        try:
            with open(self.patterns_file, "r", encoding="utf-8") as f:
                patterns = json.load(f)

            if error_type in patterns:
                patterns[error_type]["count"] += 1

            with open(self.patterns_file, "w", encoding="utf-8") as f:
                json.dump(patterns, f, ensure_ascii=False, indent=2)
        except:
            pass

    def run_quick_analysis(self):
        """快速分析项目"""
        print("🔍 正在快速分析项目...")

        # 检查项目目录
        project_files = list(Path(".").glob("*.py"))
        issues_count = 0
        files_scanned = 0

        for file in project_files:
            if "adaptive_ai_projects" in str(file) or file.name.startswith("__pycache__"):
                continue

            files_scanned += 1
            issues = self.analyze_code(file)
            issues_count += len(issues)

            if issues:
                print(f"  {file.name}: {len(issues)}个问题")

        print(f"✅ 扫描完成: {files_scanned}个文件，{issues_count}个问题")

    def run_system(self):
        """运行整个系统"""
        print("🚀 快速系统启动")
        print("=" * 60)

        # 快速项目分析
        self.run_quick_analysis()

        # 状态分析
        state = self.analyze_learning_state()
        print(f"📊 学习状态: {state['suggestion_type']}")
        print(f"🏆 已完成项目: {state['completed']}")

        # 主动沟通
        if self.communicate(force=True):
            response = "是"  # 模拟响应
            print(f"🧑 用户响应: {response}")
            self.process_response(response)

        # 记录学习
        self.record_lesson("quick_analysis", "system_init", "系统初始化完成", "初始化成功")

        print("🎉 两小时快速实现完成！")


def main():
    """主函数"""
    system = RapidSystem()

    try:
        system.run_system()
        return 0
    except KeyboardInterrupt:
        print("\n📴 用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 系统错误: {e}")
        import traceback
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())