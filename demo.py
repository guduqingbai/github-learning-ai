#!/usr/bin/env python3
"""
🎯 项目使用示例
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jarvis_monitor_noninteractive import JarvisMonitor
from hermes_integration import HermesSystem
from ai_agent_adapter import AIAgentAdapter


def run_jarvis_demo():
    """贾维斯主动沟通系统演示"""
    print("🚀 贾维斯主动沟通系统演示")
    print("=" * 60)
    
    try:
        # 创建贾维斯主动沟通系统
        jarvis = JarvisMonitor()
        
        # 显示配置信息
        print(f"📋 贾维斯系统状态: {'运行中' if jarvis.is_user_available() else '待机中'}")
        
        # 发送测试消息
        if jarvis.communicate_intelligently():
            print("✅ 贾维斯系统演示成功！")
            
    except Exception as e:
        print(f"❌ 贾维斯系统演示失败: {e}")
        
    return True


def run_hermes_demo():
    """Hermes系统集成演示"""
    print("\n🚀 Hermes系统集成演示")
    print("=" * 60)
    
    try:
        # 创建Hermes系统
        hermes = HermesSystem()
        
        # 显示系统统计信息
        report = hermes.generate_report()
        print(f"📊 Hermes系统统计: {report['data']}")
        
        # 处理项目分析任务
        project_task = {
            "type": "project_analysis",
            "keyword": "Python",
            "search_query": "Python数据分析"
        }
        
        project_results = hermes.process_task(project_task)
        
        if project_results["status"] == "success":
            print(f"✅ 找到 {len(project_results['data'])} 个项目")
            
        print("✅ Hermes系统演示成功！")
        
    except Exception as e:
        print(f"❌ Hermes系统演示失败: {e}")
        
    return True


def run_ai_agent_demo():
    """AI Agent集成演示"""
    print("\n🚀 AI Agent集成演示")
    print("=" * 60)
    
    try:
        # 创建AI Agent适配器
        adapter = AIAgentAdapter("default")
        
        # 显示配置信息
        print(f"📋 AI Agent状态: {adapter.get_agent_statistics()}")
        
        # 发送测试消息
        response = adapter.send_message("你好，请介绍一下大语言模型的最新进展")
        
        if response:
            print(f"🤖 AI Agent响应: {response}")
            
        print("✅ AI Agent集成演示成功！")
        
    except Exception as e:
        print(f"❌ AI Agent集成演示失败: {e}")
        
    return True


def main():
    """主演示函数"""
    print("🎉 GitHub学习项目演示")
    print("=" * 60)
    
    # 运行各个演示
    jarvis_ok = run_jarvis_demo()
    hermes_ok = run_hermes_demo()
    ai_agent_ok = run_ai_agent_demo()
    
    print("\n📊 演示结果")
    print("=" * 60)
    
    results = {
        "贾维斯主动沟通系统": jarvis_ok,
        "Hermes系统集成": hermes_ok,
        "AI Agent集成": ai_agent_ok
    }
    
    all_ok = True
    for name, ok in results.items():
        status = "✅" if ok else "❌"
        print(f"{status} {name}: {'成功' if ok else '失败'}")
        
        if not ok:
            all_ok = False
            
    print("\n🎯 项目特性")
    print("=" * 60)
    print("• 主动沟通: 类似钢铁侠贾维斯的主动沟通能力")
    print("• OpenClaw/Hermes Agent支持: 完整的协议和集成")
    print("• 自我学习: 系统漏洞检查和代码质量优化")
    print("• 专家系统: 8个专家角色，6个知识条目")
    print("• 多平台AI集成: OpenAI、Claude、百度、阿里云支持")
    
    if all_ok:
        print("\n🎉 项目所有功能演示成功！")
        print("📖 详细使用说明请参考README.md和USAGE.md")
        
    else:
        print("\n⚠️  部分功能演示失败，请检查系统配置")
        
    return 0


if __name__ == "__main__":
    main()
