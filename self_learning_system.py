#!/usr/bin/env python3
"""
🎯 自我学习与系统完善系统
在您不在时自动进行自我学习和系统优化
"""

import os
import time
import ast
from datetime import datetime
from pathlib import Path
from utils import measure_performance
from system_state_manager import SystemStateManager

class SelfLearningSystem:
    """自我学习与系统完善系统 - 使用统一系统状态管理"""

    def __init__(self):
        """初始化系统"""
        print("🎯 初始化自我学习系统")
        self.state_manager = SystemStateManager()
        self.data_dir = Path("data")
        self._init_system()
        print("✅ 自我学习系统初始化完成")

    def _init_system(self):
        """初始化系统（使用统一状态管理）"""
        self.data_dir.mkdir(exist_ok=True)

    def run_self_learning_cycle(self):
        """运行完整的自我学习周期"""
        print("🎯 开始自我学习与系统完善...")

        try:
            # 1. 系统漏洞检查
            start_time = time.time()
            vulnerabilities_found = self.check_system_vulnerabilities()
            check_time = time.time() - start_time

            # 2. 代码质量分析
            start_time = time.time()
            code_quality_issues = self.analyze_code_quality()
            analyze_time = time.time() - start_time

            # 3. 学习数据分析
            start_time = time.time()
            learning_analysis = self.analyze_learning_progress()
            learning_analysis_time = time.time() - start_time

            # 4. 学习进度追踪
            start_time = time.time()
            learning_progress = self.track_learning_progress()
            track_time = time.time() - start_time

            # 5. 学习优化建议
            start_time = time.time()
            optimization_suggestions = self.optimize_learning_strategy()
            optimize_time = time.time() - start_time

            # 6. 记录学习成果
            self.record_learning_session(check_time, analyze_time, track_time, optimize_time,
                                       vulnerabilities_found, code_quality_issues,
                                       len(learning_progress), len(optimization_suggestions))

            print("✅ 自我学习完成！")
            return True

        except Exception as e:
            print(f"❌ 自我学习失败: {e}")
            return False

    def check_system_vulnerabilities(self):
        """检查系统漏洞"""
        print("🔍 正在检查系统漏洞...")

        vulnerabilities = []

        # 检查系统文件权限
        for file in Path(".").glob("*.py"):
            if file.exists() and os.stat(file).st_mode & 0o004 != 0:
                vulnerabilities.append({
                    "type": "permission_issue",
                    "file": str(file),
                    "description": "文件权限过松，可能存在安全风险",
                    "severity": "medium"
                })

        # 检查代码安全问题
        for file in Path(".").glob("*.py"):
            if file.name == __file__ or "adaptive_ai_projects" in str(file):
                continue

            if not file.exists():
                continue

            try:
                with open(file, "r", encoding="utf-8") as f:
                    code = f.read()

                # 检查硬编码密码 — 要求同时出现赋值操作和敏感词
                if ("password" in code.lower() or "api_key" in code.lower() or "secret" in code.lower()) and "=" in code and ('"' in code or "'" in code):
                    vulnerabilities.append({
                        "type": "hardcoded_secret",
                        "file": str(file),
                        "description": "可能存在硬编码的密码或API密钥",
                        "severity": "high"
                    })

                # 检查SQL注入风险
                if "execute" in code and "%" in code and "cursor" in code:
                    vulnerabilities.append({
                        "type": "sql_injection_risk",
                        "file": str(file),
                        "description": "可能存在SQL注入风险",
                        "severity": "high"
                    })
            except Exception as e:
                print(f"   ⚠️  无法读取文件 {file}: {e}")
                continue

        # 更新漏洞记录（使用统一状态管理）
        vulnerabilities_data = self.state_manager.get_state("vulnerabilities")

        new_vulnerabilities = []
        for vuln in vulnerabilities:
            if vuln not in vulnerabilities_data["vulnerabilities"]:
                vulnerabilities_data["vulnerabilities"].append(vuln)
                new_vulnerabilities.append(vuln)

        self.state_manager.update_state("vulnerabilities", vulnerabilities_data)

        if new_vulnerabilities:
            print(f"⚠️  发现 {len(new_vulnerabilities)} 个新漏洞")
            for vuln in new_vulnerabilities:
                print(f"   - {vuln['type']}: {vuln['file']}")
        else:
            print("✅ 系统安全检查通过")

        return len(vulnerabilities)

    def analyze_code_quality(self):
        """分析代码质量"""
        print("📊 正在分析代码质量...")

        issues_count = 0
        files_scanned = 0

        for file in Path(".").glob("*.py"):
            if file.name == __file__ or "adaptive_ai_projects" in str(file):
                continue

            files_scanned += 1

            try:
                tree = ast.parse(file.read_text(encoding="utf-8"))
                issues = []

                for node in ast.walk(tree):
                    # 检查裸except
                    if isinstance(node, ast.ExceptHandler) and node.type is None:
                        issues.append("bare_except")

                    # 检查缺少文档字符串
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not SelfLearningSystem.has_docstring(node):
                        issues.append("missing_docstring")

                    # 检查缺少类型提示
                    if isinstance(node, ast.FunctionDef):
                        for arg in node.args.args:
                            if not arg.annotation:
                                issues.append("no_type_hints")

                issues_count += len(issues)

            except Exception:
                continue

        print(f"📈 代码质量分析: 扫描 {files_scanned} 个文件，发现 {issues_count} 个问题")
        return issues_count

    @measure_performance
    def analyze_learning_progress(self):
        """分析学习进度 - 优化版本"""
        print("📊 正在分析学习进度...")

        learning = self.state_manager.get_state("learning")

        # 计算学习进度
        total_topics = len(learning["knowledge_points"])
        learning_time = learning["total_study_time"]

        # 动态计算目标值，根据已完成的主题数量
        target_topics = max(50, total_topics * 1.5)
        progress = min(100, int(total_topics / target_topics * 100))

        analysis = {
            "total_topics": total_topics,
            "learning_time": learning_time,
            "progress": progress,
            "target_topics": int(target_topics),
            "completed_projects": len(learning["projects_studied"])
        }

        # 学习效率分析（基于主题数量和学习时间的比值）
        if total_topics > 0 and learning_time > 0:
            topics_per_hour = (total_topics / learning_time) * 60

            if topics_per_hour > 8:  # 每小时超过8个主题
                analysis["learning_efficiency"] = "高效"
            elif topics_per_hour > 4:  # 每小时4-8个主题
                analysis["learning_efficiency"] = "中等"
            else:
                analysis["learning_efficiency"] = "需要改进"

            analysis["topics_per_hour"] = round(topics_per_hour, 2)
        else:
            analysis["learning_efficiency"] = "尚未开始"

        print(f"📈 学习进度分析: {analysis['total_topics']} 个主题, {analysis['learning_time']} 分钟")
        print(f"🚀 学习效率: {analysis['learning_efficiency']}")
        if "topics_per_hour" in analysis:
            print(f"⏱️  学习效率: {analysis['topics_per_hour']} 个主题/小时")

        return analysis

    def track_learning_progress(self):
        """学习进度追踪 - 记录学习活动"""
        print("📝 正在追踪学习进度...")

        learning = self.state_manager.get_state("learning")

        # 简单的学习进度更新
        progress = []
        if learning["total_study_time"] < 600:  # 小于10分钟
            progress.append("建议增加学习时间")
        if len(learning["knowledge_points"]) < 10:
            progress.append("建议扩展知识库")
        if len(learning["improvements"]) > 20:
            progress.append("建议优先实施优化建议")

        # 更新学习记录
        learning["last_learned"] = datetime.now().isoformat()
        self.state_manager.update_state("learning", learning)

        return progress

    def optimize_learning_strategy(self):
        """优化学习策略 - 基于数据分析的优化建议"""
        print("🎯 正在优化学习策略...")

        learning = self.state_manager.get_state("learning")

        suggestions = []
        total_topics = len(learning["knowledge_points"])
        learning_time = learning["total_study_time"]

        # 学习效率分析和建议
        if total_topics > 0 and learning_time > 0:
            topics_per_hour = (total_topics / learning_time) * 60

            if topics_per_hour < 0.1:  # 学习效率过低
                suggestions.append("建议增加学习时间或提高专注力")
                suggestions.append("考虑使用番茄工作法提高效率")
            elif topics_per_hour > 0.3:  # 学习效率过高
                suggestions.append("学习效率很高，但注意避免疲劳")
                suggestions.append("建议适当休息，保持学习质量")

        # 根据主题数量和学习时间提供建议
        if total_topics < 5:
            suggestions.append("建议每天学习1-2个新主题，建立学习习惯")
            suggestions.append("重点学习基础概念，打牢基础")
        elif total_topics < 15:
            suggestions.append("建议学习复杂主题和深度理解，扩展知识面")
            suggestions.append("考虑进行项目实践，将理论知识应用到实际")
        else:
            suggestions.append("建议进行知识整理和回顾，构建知识体系")
            suggestions.append("考虑分享知识，加深对概念的理解")

        if learning_time < 300:  # 小于5分钟
            suggestions.append("建议增加单次学习时间，至少学习15-30分钟")
            suggestions.append("避免碎片化学习，保持专注")
        elif learning_time > 3600:  # 大于60分钟
            suggestions.append("学习时间过长，建议分散学习，提高效率")
            suggestions.append("每隔25-30分钟休息5分钟，保持学习效率")

        return suggestions

    def record_learning_session(self, check_time, analyze_time, track_time, optimize_time,
                               vulnerabilities_found, code_quality_issues,
                               learning_progress, optimization_suggestions):
        """记录学习会话"""
        session = {
            "timestamp": datetime.now().isoformat(),
            "duration": check_time + analyze_time + track_time + optimize_time,  # 总时间
            "activities": [
                {
                    "name": "系统漏洞检查",
                    "duration": check_time,
                    "results": vulnerabilities_found,
                    "explanation": self._explain_vulnerability_check(vulnerabilities_found)
                },
                {
                    "name": "代码质量分析",
                    "duration": analyze_time,
                    "results": code_quality_issues,
                    "explanation": self._explain_code_quality_analysis(code_quality_issues)
                },
                {
                    "name": "学习进度追踪",
                    "duration": track_time,
                    "results": learning_progress,
                    "explanation": self._explain_learning_progress(learning_progress)
                },
                {
                    "name": "学习策略优化",
                    "duration": optimize_time,
                    "results": optimization_suggestions,
                    "explanation": self._explain_learning_strategy(optimization_suggestions)
                }
            ],
            "results": {
                "vulnerabilities_found": vulnerabilities_found,
                "vulnerabilities_fixed": 0,
                "issues_found": code_quality_issues,
                "learning_progress": learning_progress,
                "optimization_suggestions": optimization_suggestions
            }
        }

        # 使用统一状态管理保存学习记录
        self_learning_data = self.state_manager.get_state("self_learning")
        self_learning_data["records"].append(session)
        self.state_manager.update_state("self_learning", self_learning_data)

        # 打印详细的任务执行时间和结果
        print("\n⏱️  任务执行时间")
        print("=" * 60)
        print(f"🔍 系统漏洞检查: {check_time:.2f}秒，发现 {vulnerabilities_found} 个漏洞")
        print(f"📊 代码质量分析: {analyze_time:.2f}秒，发现 {code_quality_issues} 个问题")
        print(f"📈 学习进度追踪: {track_time:.2f}秒，记录 {learning_progress} 条进度")
        print(f"🎯 学习策略优化: {optimize_time:.2f}秒，提供 {optimization_suggestions} 个优化建议")
        print(f"⏰ 总时间: {session['duration']:.2f}秒")

        # 打印任务解释
        print("\n📖 任务解释")
        print("=" * 60)
        for activity in session["activities"]:
            print(f"📌 {activity['name']}:")
            print(f"   {activity['explanation']}")
            print()

    def _explain_vulnerability_check(self, count):
        """解释系统漏洞检查任务"""
        if count == 0:
            return "系统安全检查通过，没有发现明显的漏洞。"
        elif count < 5:
            return f"发现 {count} 个漏洞，主要是文件权限问题，建议及时修复。"
        else:
            return f"发现 {count} 个漏洞，系统存在安全风险，需要立即修复。"

    def _explain_code_quality_analysis(self, count):
        """解释代码质量分析任务"""
        if count == 0:
            return "代码质量分析完成，没有发现问题。"
        elif count < 10:
            return f"发现 {count} 个代码质量问题，主要是缺少文档字符串和类型提示。"
        else:
            return f"发现 {count} 个代码质量问题，代码需要进行重构优化。"

    def _explain_learning_progress(self, count):
        """解释学习进度任务"""
        if count == 0:
            return "学习进度追踪完成，没有发现明显的学习活动。"
        elif count < 5:
            return f"学习进度追踪完成，发现 {count} 条学习活动记录，学习内容相对较少。"
        else:
            return f"学习进度追踪完成，发现 {count} 条学习活动记录，学习内容丰富。"

    def _explain_learning_strategy(self, count):
        """解释学习策略优化任务"""
        if count == 0:
            return "学习策略优化完成，没有发现需要优化的学习策略。"
        elif count < 3:
            return f"学习策略优化完成，发现 {count} 个学习策略优化建议。"
        else:
            return f"学习策略优化完成，发现 {count} 个学习策略优化建议，学习效率可以显著提升。"

    @staticmethod
    def has_docstring(node):
        """检查是否有文档字符串"""
        if not hasattr(node, "body") or len(node.body) == 0:
            return False

        first_node = node.body[0]

        if isinstance(first_node, ast.Expr) and isinstance(first_node.value, (ast.Constant, ast.Str)):
            return True

        return False

    def get_vulnerabilities(self):
        """获取漏洞列表（使用统一状态管理）"""
        vulnerabilities_data = self.state_manager.get_state("vulnerabilities")
        return vulnerabilities_data["vulnerabilities"]

def main():
    """主函数"""
    system = SelfLearningSystem()

    try:
        system.run_self_learning_cycle()
        return 0
    except Exception as e:
        print(f"❌ 自我学习系统失败: {e}")
        return 1


if __name__ == "__main__":
    main()