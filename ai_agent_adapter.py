#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent智能体适配器 - 支持多种AI Agent平台
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

class AIAgentAdapter:
    """AI Agent智能体适配器 - 支持多平台集成"""

    def __init__(self, platform="default"):
        """初始化AI Agent适配器"""
        self.platform = platform
        self.agent_config = self._load_agent_config()
        self.claude_code_adapter = None

        # 如果是Claude Code平台，初始化专门的适配器
        if platform == "claude-code":
            try:
                from claude_code_adapter import ClaudeCodeAdapter
                self.claude_code_adapter = ClaudeCodeAdapter()
            except ImportError as e:
                print(f"⚠️  无法加载Claude Code适配器: {e}")

    def _load_agent_config(self):
        """加载AI Agent配置"""
        config_file = Path("data") / "ai_agent_config.json"

        default_config = {
            "platform": "default",
            "api_key": "",
            "base_url": "",
            "agent_id": "",
            "timeout": 30,
            "retries": 3
        }

        if not config_file.exists():
            self._save_agent_config(default_config)
            return default_config

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  加载AI Agent配置失败: {e}")
            return default_config

    def _save_agent_config(self, config):
        """保存AI Agent配置"""
        config_file = Path("data") / "ai_agent_config.json"

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print("✅ AI Agent配置已保存")
        except Exception as e:
            print(f"❌ 保存AI Agent配置失败: {e}")

    def update_agent_config(self, platform, api_key, base_url="", agent_id=""):
        """更新AI Agent配置"""
        config = {
            "platform": platform,
            "api_key": api_key,
            "base_url": base_url,
            "agent_id": agent_id,
            "timeout": 30,
            "retries": 3
        }

        self.agent_config = config
        self._save_agent_config(config)
        self.platform = platform

    def is_agent_available(self):
        """检查AI Agent是否可用"""
        return self.agent_config["api_key"] != ""

    def send_message(self, message, context=None):
        """发送消息到AI Agent"""
        if not self.is_agent_available():
            print("⚠️  AI Agent不可用，请先配置API密钥")
            return None

        print(f"📩 发送消息到AI Agent ({self.platform})")

        try:
            if self.platform == "openai":
                return self._send_to_openai(message, context)
            elif self.platform == "claude":
                return self._send_to_claude(message, context)
            elif self.platform == "claude-code":
                return self._send_to_claude_code(message, context)
            elif self.platform == "baidu":
                return self._send_to_baidu(message, context)
            elif self.platform == "aliyun":
                return self._send_to_aliyun(message, context)
            else:
                return self._send_to_default_agent(message, context)

        except Exception as e:
            print(f"❌ 发送消息失败: {e}")
            return None

    def _send_to_openai(self, message, context):
        """发送到OpenAI的GPT模型"""
        url = self.agent_config["base_url"] or "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.agent_config['api_key']}"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "你是一个专业的AI学习助手，帮助用户学习和解决问题。"},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7
        }

        if context:
            data["messages"].insert(1, {"role": "system", "content": context})

        response = requests.post(url, headers=headers, json=data, timeout=self.agent_config["timeout"])
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    def _send_to_claude(self, message, context):
        """发送到Anthropic的Claude模型"""
        url = self.agent_config["base_url"] or "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.agent_config["api_key"]
        }

        data = {
            "model": "claude-3-sonnet-20250219",
            "messages": [
                {"role": "user", "content": message}
            ],
            "temperature": 0.7
        }

        if context:
            data["messages"].insert(0, {"role": "system", "content": context})

        response = requests.post(url, headers=headers, json=data, timeout=self.agent_config["timeout"])
        response.raise_for_status()

        return response.json()["content"][0]["text"]

    def _send_to_claude_code(self, message, context):
        """发送到Claude Code平台"""
        if self.claude_code_adapter:
            # 如果是代码相关任务，使用专门的代码分析方法
            if any(keyword in message.lower() for keyword in ["代码", "质量", "优化", "分析"]):
                try:
                    code_start = message.find("```")
                    code_end = message.rfind("```")
                    if code_start != -1 and code_end != -1:
                        code = message[code_start + 3:code_end].strip()
                        if len(code) > 50:
                            quality_report = self.claude_code_adapter.analyze_code_quality(code)
                            if quality_report:
                                return json.dumps(quality_report, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"⚠️  Claude Code代码分析失败: {e}")

            return self.claude_code_adapter.create_code_suggestions(message)

        print("⚠️  Claude Code适配器未初始化")
        return self._send_to_claude(message, context)

    def _send_to_baidu(self, message, context):
        """发送到百度的文心一言模型"""
        # 百度API使用方式类似，需要根据实际API调整
        pass

    def _send_to_aliyun(self, message, context):
        """发送到阿里云的通义千问模型"""
        # 阿里云API使用方式类似，需要根据实际API调整
        pass

    def _send_to_default_agent(self, message, context):
        """默认AI Agent处理"""
        default_response = {
            "收到消息": message,
            "上下文": context,
            "处理时间": datetime.now().isoformat(),
            "平台": self.platform
        }

        print(json.dumps(default_response, ensure_ascii=False, indent=2))
        return json.dumps(default_response, ensure_ascii=False)

    def get_agent_response(self, user_input):
        """获取AI Agent的响应"""
        if not self.is_agent_available():
            return None

        context = self._prepare_context()
        response = self.send_message(user_input, context)

        if response:
            print(f"✅ AI Agent响应: {response[:100]}...")

        return response

    def _prepare_context(self):
        """准备沟通上下文"""
        context = []

        # 加载用户状态
        try:
            with open(Path("data") / "active_state.json", "r", encoding="utf-8") as f:
                active_state = json.load(f)

            context.append(f"用户已完成项目: {active_state.get('projects_completed', 0)}个")
            context.append(f"学习目标: {active_state.get('current_goal', '未设置')}")

        except Exception as e:
            print(f"⚠️  加载用户状态失败: {e}")

        # 加载学习进度
        try:
            with open(Path("data") / "learning_progress.json", "r", encoding="utf-8") as f:
                learning = json.load(f)

            context.append(f"学习时间: {learning.get('total_study_time', 0)}分钟")
            context.append(f"学习项目: {len(learning.get('projects_studied', []))}个")

        except Exception as e:
            print(f"⚠️  加载学习进度失败: {e}")

        return "\n".join(context)

    def create_agent_command(self, command_type, params=None):
        """创建AI Agent命令"""
        commands = {
            "analyze_code": "分析项目代码质量",
            "check_vulnerability": "检查系统漏洞",
            "optimize_system": "优化系统性能",
            "search_knowledge": "搜索AI知识",
            "generate_suggestion": "生成学习建议",
            "update_knowledge": "更新知识库"
        }

        if command_type not in commands:
            return f"未知命令类型: {command_type}"

        return f"请执行命令: {commands[command_type]}"

    def execute_agent_command(self, command_type, params=None):
        """执行AI Agent命令"""
        # 如果是Claude Code平台，处理代码分析相关命令
        if self.platform == "claude-code":
            if command_type == "analyze_code":
                if params and "code" in params:
                    return self.claude_code_adapter.analyze_code_quality(
                        params["code"],
                        params.get("filename"),
                        params.get("language")
                    )
            elif command_type == "optimize_code":
                if params and "code" in params:
                    return self.claude_code_adapter.optimize_code(
                        params["code"],
                        params.get("filename"),
                        params.get("language"),
                        params.get("optimization_level", "medium")
                    )
            elif command_type == "find_issues":
                if params and "code" in params:
                    return self.claude_code_adapter.find_code_issues(
                        params["code"],
                        params.get("filename"),
                        params.get("language")
                    )
            elif command_type == "suggest_optimizations":
                if params and "code" in params:
                    return self.claude_code_adapter.suggest_optimizations(
                        params["code"],
                        params.get("filename"),
                        params.get("language")
                    )
            elif command_type == "analyze_project":
                if params and "path" in params:
                    return self.claude_code_adapter.analyze_project_structure(
                        params["path"]
                    )
            elif command_type == "create_suggestion":
                if params and "requirements" in params:
                    return self.claude_code_adapter.create_code_suggestions(
                        params["requirements"],
                        params.get("language", "Python")
                    )

        command = self.create_agent_command(command_type, params)
        response = self.get_agent_response(command)

        return response

    def update_agent_knowledge(self, knowledge_items):
        """更新AI Agent的知识库"""
        if not self.is_agent_available():
            return False

        print("📚 更新AI Agent知识库")

        try:
            knowledge_text = "\n".join([f"- {item}" for item in knowledge_items])
            message = f"请将以下知识添加到知识库中:\n{knowledge_text}"

            response = self.get_agent_response(message)

            return response is not None

        except Exception as e:
            print(f"❌ 更新知识库失败: {e}")
            return False

    def get_agent_statistics(self):
        """获取AI Agent统计信息"""
        return {
            "平台": self.platform,
            "是否可用": self.is_agent_available(),
            "API密钥配置": self.agent_config["api_key"] != "",
            "超时设置": self.agent_config["timeout"],
            "重试次数": self.agent_config["retries"]
        }

def main():
    """测试AI Agent适配器"""
    print("🚀 测试AI Agent适配器")
    print("=" * 60)

    try:
        # 创建AI Agent适配器
        adapter = AIAgentAdapter("default")

        # 显示当前配置
        print("📋 当前AI Agent配置:")
        stats = adapter.get_agent_statistics()
        for key, value in stats.items():
            print(f"   {key}: {value}")

        # 测试发送消息
        print("\n📝 测试发送消息:")
        response = adapter.send_message("请介绍一下AI Agent智能体的发展趋势")

        if response:
            print(f"✅ 成功收到响应")
            print(f"📄 响应内容: {response[:200]}...")
        else:
            print("⚠️  未收到响应")

        print("\n✅ 测试完成!")
        return 0

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    main()
