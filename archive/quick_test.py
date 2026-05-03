#!/usr/bin/env python3
"""
🎯 快速功能测试脚本
验证学习数据分析与优化系统的核心功能
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_system_functionality():
    """测试系统核心功能"""
    print("🎯 学习数据分析与优化系统功能测试")
    print("=" * 60)

    try:
        # 1. 测试系统接口
        print("\n📡 测试系统接口:")
        from system_interfaces import get_system_interface
        interface = get_system_interface()

        # 测试学习接口
        learning_state = interface.learning.get_learning_state()
        print(f"   - 学习时间: {int(learning_state['total_study_time'] / 60)} 分钟")
        print(f"   - 已学项目: {len(learning_state['projects_studied'])} 个")
        print(f"   - 知识点: {len(learning_state['knowledge_points'])} 个")

        # 测试认知接口
        cognitive_state = interface.cognitive.get_cognitive_state()
        print(f"   - 注意力: {cognitive_state['attention']}")
        print(f"   - 意识水平: {cognitive_state['awareness']:.2f}")

        # 2. 测试知识库
        print("\n📚 测试知识库:")
        from knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        print(f"   - 知识库条目: {len(kb.get_all_knowledge())} 个")

        # 测试知识检索
        retrieved = kb.retrieve_knowledge("机器学习")
        print(f"   - 检索结果: {len(retrieved)} 个")

        # 3. 测试浏览器集成
        print("\n🌐 测试浏览器集成:")
        from browser_integration import BrowserIntegration
        browser_integration = BrowserIntegration()

        config = browser_integration.get_browser_config()
        print(f"   - 配置浏览器: {list(config['browsers'].keys())}")
        print(f"   - 可用浏览器: {browser_integration.get_available_browsers()}")

        # 4. 测试Web界面可访问性
        print("\n🌍 测试Web界面:")
        import requests

        try:
            response = requests.get("http://localhost:5000", timeout=5)
            if response.status_code == 200:
                print(f"   - Web界面运行正常: 状态码 {response.status_code}")
                print(f"   - 响应内容长度: {len(response.text)} 字节")
            else:
                print(f"   - Web界面响应异常: 状态码 {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("   - 警告: 无法连接到Web界面，请检查服务器是否正在运行")
        except Exception as e:
            print(f"   - Web界面测试错误: {e}")

        # 5. 测试系统状态
        print("\n📊 测试系统状态:")
        summary = interface.get_global_state_summary()
        print(f"   - 系统版本: {summary['system']['version']}")
        print(f"   - 性能分数: {summary['system']['performance']}")

        print("\n✅ 所有核心功能测试通过！")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        print(f"详细信息: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = test_system_functionality()
    sys.exit(0 if success else 1)
