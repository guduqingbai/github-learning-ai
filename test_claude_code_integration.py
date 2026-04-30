#!/usr/bin/env python3
"""
🧪 测试Claude Code集成功能
验证Claude Code适配器与AI代理接口的集成
"""

import os
import sys
import json
import time
from pathlib import Path
from ai_agent_adapter import AIAgentAdapter
from claude_code_adapter import ClaudeCodeAdapter


def test_claude_code_adapter():
    """测试Claude Code适配器"""
    print("🧪 测试Claude Code适配器")
    print("=" * 60)

    try:
        adapter = ClaudeCodeAdapter()

        print("📊 测试基本配置...")
        if adapter.is_available():
            print("✅ Claude Code API密钥已配置")
        else:
            print("⚠️  Claude Code API密钥未配置，请检查config.json")

        print("\n📝 测试代码质量分析...")
        test_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total

def main():
    data = [1, 2, 3, 4, 5]
    result = calculate_total(data)
    print(f"Total: {result}")

if __name__ == "__main__":
    main()
"""
        quality = adapter.analyze_code_quality(test_code, "test.py", "Python")
        if quality:
            print(f"✅ 代码质量分析成功")
            print(f"   总体评分: {quality.get('score', 'N/A')}")
            for dimension, score in quality.get('dimensions', {}).items():
                print(f"   • {dimension}: {score}")
            if quality.get('suggestions'):
                print(f"   改进建议: {len(quality['suggestions'])} 条")

        print("\n🔍 测试代码问题检测...")
        issues = adapter.find_code_issues(test_code)
        if issues:
            print(f"✅ 代码问题检测成功")
            # 检查是否是字符串还是列表
            if isinstance(issues, list):
                for issue in issues:
                    if isinstance(issue, dict) and 'severity' in issue and 'description' in issue:
                        print(f"   • [{issue['severity']}] {issue['description']}")
            elif isinstance(issues, dict):
                print("   响应格式: 单问题")
            else:
                print(f"   响应内容: {issues}")

        print("\n🔧 测试代码优化建议...")
        suggestions = adapter.suggest_optimizations(test_code)
        if suggestions:
            print(f"✅ 代码优化建议成功")
            # 检查响应类型
            if isinstance(suggestions, list):
                for index, suggestion in enumerate(suggestions):
                    if isinstance(suggestion, dict):
                        priority = suggestion.get('priority', 'medium')
                        type_ = suggestion.get('type', '优化')
                        desc = suggestion.get('description', '无描述')
                        print(f"   • [{priority}] {type_}: {desc}")
                    elif isinstance(suggestion, str):
                        print(f"   • 建议: {suggestion}")
                    else:
                        print(f"   • {suggestion}")
            elif isinstance(suggestions, dict):
                print("   响应格式: 单建议")
            else:
                print(f"   响应内容: {suggestions}")

        print("\n📈 测试项目结构分析...")
        current_path = Path(".")
        project_analysis = adapter.analyze_project_structure(str(current_path))
        if project_analysis:
            print(f"✅ 项目结构分析成功")
            print(f"   架构评分: {project_analysis.get('score', 'N/A')}")
            if project_analysis.get('suggestions'):
                print(f"   优化建议: {len(project_analysis['suggestions'])} 条")

        print("\n💡 测试代码建议生成...")
        requirements = "创建一个简单的文件管理工具，支持文件搜索、内容读取和写入功能"
        code_suggestion = adapter.create_code_suggestions(requirements, "Python")
        if code_suggestion:
            print("✅ 代码建议生成成功")
            print("📄 代码建议片段:")
            print(code_suggestion[:200] + "...")

        print("\n✅ Claude Code适配器测试完成！")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False


def test_ai_agent_integration():
    """测试AI代理接口与Claude Code的集成"""
    print("\n🧪 测试AI代理接口集成")
    print("=" * 60)

    try:
        print("🔌 测试Claude Code集成模式...")
        adapter = AIAgentAdapter("claude-code")

        print("📊 配置信息:")
        print(f"   平台: {adapter.platform}")
        print(f"   是否可用: {'✅ 可用' if adapter.is_agent_available() else '⚠️  不可用'}")
        if hasattr(adapter, 'claude_code_adapter') and adapter.claude_code_adapter:
            print(f"   Claude Code适配器: ✅ 已初始化")

        print("\n📝 测试消息发送...")
        test_message = "请提供一个简单的Python函数示例，用于计算列表中数字的平均值"
        response = adapter.send_message(test_message)
        if response:
            print(f"✅ 消息发送成功")
            print("📄 响应:")
            print(response)

        print("\n🎯 测试代码分析命令...")
        test_code = """
def average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
"""
        command_response = adapter.execute_agent_command("analyze_code",
                                                       {"code": test_code, "filename": "test.py", "language": "Python"})
        if command_response:
            print("✅ 代码分析命令成功")
            if isinstance(command_response, dict):
                print(f"   评分: {command_response.get('score', 'N/A')}")
            else:
                print(command_response)

        print("\n✅ AI代理接口集成测试完成！")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False


def test_code_optimization():
    """测试代码优化功能"""
    print("\n🧪 测试代码优化功能")
    print("=" * 60)

    try:
        adapter = ClaudeCodeAdapter()

        print("📊 测试代码优化...")
        test_code = """
def find_duplicates(arr):
    duplicates = []
    seen = set()
    for num in arr:
        if num in seen and num not in duplicates:
            duplicates.append(num)
        seen.add(num)
    return duplicates

def main():
    data = [1, 2, 3, 2, 4, 5, 3, 6, 7, 8, 7]
    duplicates = find_duplicates(data)
    print(f"Duplicates: {duplicates}")

if __name__ == "__main__":
    main()
"""

        quality = adapter.analyze_code_quality(test_code, "optimization_test.py", "Python")
        if quality:
            print(f"原始代码质量: {quality.get('score', 'N/A')}")

        print("\n🔧 优化代码...")
        optimization_result = adapter.optimize_code(test_code, "optimization_test.py", "Python")
        if optimization_result:
            print("✅ 代码优化成功")
            if 'optimized_code' in optimization_result:
                print("优化后的代码:")
                print(optimization_result['optimized_code'])
            if 'performance_improvement' in optimization_result:
                print(f"性能提升: {optimization_result['performance_improvement']}%")

        print("\n✅ 代码优化功能测试完成！")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False


def test_project_structure_analysis():
    """测试项目结构分析功能"""
    print("\n🧪 测试项目结构分析")
    print("=" * 60)

    try:
        adapter = ClaudeCodeAdapter()

        current_path = Path(".")
        print(f"📊 分析项目结构: {current_path}")

        analysis = adapter.analyze_project_structure(str(current_path))
        if analysis:
            print("✅ 项目结构分析成功")
            print(f"   架构评分: {analysis.get('score', 'N/A')}")

            if 'suggestions' in analysis and analysis['suggestions']:
                print("\n📋 优化建议:")
                for suggestion in analysis['suggestions']:
                    print(f"   • {suggestion}")

            if 'dependencies' in analysis:
                print(f"\n🔗 依赖分析: {analysis['dependencies']}")

        print("\n✅ 项目结构分析测试完成！")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始Claude Code集成功能测试")
    print("=" * 60)

    # 测试结果记录
    test_results = {
        "timestamp": time.time(),
        "tests": []
    }

    tests = [
        ("Claude Code适配器", test_claude_code_adapter),
        ("AI代理集成", test_ai_agent_integration),
        ("代码优化功能", test_code_optimization),
        ("项目结构分析", test_project_structure_analysis)
    ]

    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        start_time = time.time()
        success = test_func()
        end_time = time.time()

        test_results["tests"].append({
            "name": test_name,
            "success": success,
            "duration": end_time - start_time
        })

    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)

    for test in test_results["tests"]:
        status = "✅ 成功" if test["success"] else "❌ 失败"
        duration = f"{test['duration']:.2f}秒"
        print(f"{test['name']}: {status} ({duration})")

    # 保存测试结果
    results_file = Path("data") / "claude_code_integration_test_results.json"
    os.makedirs("data", exist_ok=True)

    try:
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 测试结果已保存到: {results_file}")
    except Exception as e:
        print(f"\n⚠️  保存测试结果失败: {e}")

    # 统计成功和失败的测试数量
    success_count = sum(1 for test in test_results["tests"] if test["success"])
    failure_count = len(tests) - success_count

    print(f"\n🎯 测试统计: 成功 {success_count}/{len(tests)}, 失败 {failure_count}/{len(tests)}")

    if failure_count > 0:
        print("⚠️  有测试失败，请检查配置或代码")
        return False
    else:
        print("🎉 所有测试通过！Claude Code集成功能正常")
        return True


if __name__ == "__main__":
    main()
