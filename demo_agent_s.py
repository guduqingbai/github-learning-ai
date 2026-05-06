"""
🤖 Agent-S Demo — 让自我思考系统动手操作电脑
运行: python demo_agent_s.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agent_s_bridge import AgentSBridge


def demo_simple_task():
    """Demo 1: 打开记事本并输入文字"""
    print("=" * 50)
    print("Demo 1: 打开记事本并输入文字")
    print("=" * 50)

    bridge = AgentSBridge(engine_params={
        "engine_type": "openai",
        "model": "gpt-4o",
    })

    ok = bridge.initialize()
    if not ok:
        print("❌ Agent-S 初始化失败（可能是没有 API Key）")
        print("   设置环境变量 OPENAI_API_KEY 后再试")
        return False

    result = bridge.execute("打开记事本，输入'你好，我是自我思考AI系统'")
    print(f"\n结果: {'✅ 成功' if result.get('success') else '❌ 失败'}")
    print(f"   执行步数: {result.get('actions_taken', 0)}")
    if result.get('error'):
        print(f"   错误: {result['error']}")

    bridge.close()
    return True


def demo_with_self_thinking():
    """Demo 2: 通过 self-thinking 系统触发"""
    print("=" * 50)
    print("Demo 2: 通过自我思考系统调度")
    print("=" * 50)

    from self_thinking_agent import SelfThinkingAgent
    agent = SelfThinkingAgent()

    # 设置待执行的任务
    agent._agent_s_tasks = [
        "打开计算器",
        "在桌面创建一个 test_hello.txt 文件，写入 Agent-S 已集成",
    ]

    # 触发 computer_use 技能
    results = agent.run_skill("computer_use", depth=2)
    print(f"\n完成 {len(results)} 个任务")


if __name__ == "__main__":
    print("🤖 Agent-S 集成 Demo")
    print()

    if "--full" in sys.argv:
        demo_with_self_thinking()
    else:
        demo_simple_task()

    print()
    print("💡 提示: 运行 python demo_agent_s.py --full 体验完整集成流程")
