#!/usr/bin/env python3
"""
🚀 Hermes Agent OpenClaw协议解析器
实现OpenClaw/Hermes协议的解析和生成
"""

import json
import time
import hashlib
from typing import Dict, Any, Optional

class HermesProtocol:
    """
    Hermes Agent协议解析器

    提供OpenClaw/Hermes协议的解析和响应生成功能
    """

    def __init__(self, protocol_version: str = "1.0"):
        """
        初始化协议解析器

        Args:
            protocol_version: 协议版本
        """
        self.protocol_version = protocol_version
        self.message_types = {
            "query": "查询消息",
            "response": "响应消息",
            "command": "命令消息",
            "event": "事件消息",
            "error": "错误消息"
        }

    def parse_message(self, raw_message: str) -> Dict[str, Any]:
        """
        解析协议消息

        Args:
            raw_message: 原始协议消息字符串

        Returns:
            解析后的消息字典

        Raises:
            ValueError: 消息格式错误
            Exception: 其他解析错误
        """
        try:
            message = json.loads(raw_message)

            # 验证消息格式
            self._validate_message(message)

            return message

        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析错误: {e}")
        except Exception as e:
            raise Exception(f"消息解析失败: {e}")

    def generate_response(self,
                        request_id: str,
                        data: Any,
                        status: str = "success") -> str:
        """
        生成协议响应

        Args:
            request_id: 请求ID
            data: 响应数据
            status: 响应状态

        Returns:
            协议响应字符串
        """
        response = {
            "version": self.protocol_version,
            "type": "response",
            "request_id": request_id,
            "timestamp": int(time.time() * 1000),
            "status": status,
            "data": data
        }

        return json.dumps(response, ensure_ascii=False, indent=2)

    def generate_query(self,
                     query_type: str,
                     data: Any,
                     metadata: Dict[str, Any] = None) -> str:
        """
        生成查询消息

        Args:
            query_type: 查询类型
            data: 查询数据
            metadata: 元数据

        Returns:
            查询消息字符串
        """
        message = {
            "version": self.protocol_version,
            "type": "query",
            "request_id": self._generate_request_id(),
            "timestamp": int(time.time() * 1000),
            "query_type": query_type,
            "data": data
        }

        if metadata:
            message["metadata"] = metadata

        return json.dumps(message, ensure_ascii=False, indent=2)

    def generate_command(self,
                       command_type: str,
                       command: str,
                       params: Dict[str, Any],
                       metadata: Dict[str, Any] = None) -> str:
        """
        生成命令消息

        Args:
            command_type: 命令类型
            command: 命令名称
            params: 命令参数
            metadata: 元数据

        Returns:
            命令消息字符串
        """
        message = {
            "version": self.protocol_version,
            "type": "command",
            "request_id": self._generate_request_id(),
            "timestamp": int(time.time() * 1000),
            "command_type": command_type,
            "command": command,
            "params": params
        }

        if metadata:
            message["metadata"] = metadata

        return json.dumps(message, ensure_ascii=False, indent=2)

    def generate_event(self,
                     event_type: str,
                     data: Any,
                     source: str = "system") -> str:
        """
        生成事件消息

        Args:
            event_type: 事件类型
            data: 事件数据
            source: 事件源

        Returns:
            事件消息字符串
        """
        message = {
            "version": self.protocol_version,
            "type": "event",
            "timestamp": int(time.time() * 1000),
            "event_type": event_type,
            "data": data,
            "source": source
        }

        return json.dumps(message, ensure_ascii=False, indent=2)

    def generate_error(self,
                     request_id: str,
                     error_code: str,
                     error_message: str,
                     details: Any = None) -> str:
        """
        生成错误消息

        Args:
            request_id: 请求ID
            error_code: 错误码
            error_message: 错误消息
            details: 详细错误信息

        Returns:
            错误消息字符串
        """
        error = {
            "version": self.protocol_version,
            "type": "error",
            "request_id": request_id,
            "timestamp": int(time.time() * 1000),
            "error_code": error_code,
            "error_message": error_message
        }

        if details:
            error["details"] = details

        return json.dumps(error, ensure_ascii=False, indent=2)

    def _validate_message(self, message: Dict[str, Any]):
        """
        验证消息格式

        Args:
            message: 消息字典

        Raises:
            ValueError: 格式验证失败
        """
        required_fields = ["version", "type", "timestamp"]

        for field in required_fields:
            if field not in message:
                raise ValueError(f"缺少必填字段: {field}")

        if message["version"] != self.protocol_version:
            raise ValueError(f"协议版本不匹配: 期望 {self.protocol_version}, 实际 {message['version']}")

        if message["type"] not in self.message_types:
            raise ValueError(f"未知消息类型: {message['type']}")

        if message["timestamp"] < (time.time() - 300) * 1000:
            raise ValueError("消息已过期")

    def _generate_request_id(self) -> str:
        """
        生成唯一请求ID

        Returns:
            唯一请求ID
        """
        timestamp = str(int(time.time() * 1000))
        random_part = str(hash(timestamp + str(id(self))))[-8:]

        return f"req_{timestamp}_{random_part}"

    def validate_checksum(self, message: str, checksum: str) -> bool:
        """
        验证消息校验和

        Args:
            message: 消息内容
            checksum: 预期的校验和

        Returns:
            校验是否通过
        """
        computed_checksum = hashlib.sha256(message.encode('utf-8')).hexdigest()

        return computed_checksum == checksum

    def compute_checksum(self, message: str) -> str:
        """
        计算消息校验和

        Args:
            message: 消息内容

        Returns:
            校验和字符串
        """
        return hashlib.sha256(message.encode('utf-8')).hexdigest()


class HermesInterface:
    """
    Hermes Agent接口类

    提供与Hermes系统交互的高级接口
    """

    def __init__(self, protocol: HermesProtocol):
        """
        初始化接口

        Args:
            protocol: 协议解析器
        """
        self.protocol = protocol
        self.connection_status = "disconnected"

    def connect(self, endpoint: str) -> bool:
        """
        连接到Hermes系统

        Args:
            endpoint: 连接端点

        Returns:
            是否连接成功
        """
        try:
            # 模拟连接过程
            print(f"连接到Hermes系统: {endpoint}")
            time.sleep(0.5)

            self.connection_status = "connected"
            print("✅ 成功连接到Hermes系统")

            return True

        except Exception as e:
            print(f"❌ 连接失败: {e}")
            self.connection_status = "disconnected"
            return False

    def disconnect(self):
        """
        断开连接
        """
        self.connection_status = "disconnected"
        print("🔌 已断开与Hermes系统的连接")

    def send_query(self, query_type: str, data: Any) -> Dict[str, Any]:
        """
        发送查询并接收响应

        Args:
            query_type: 查询类型
            data: 查询数据

        Returns:
            响应数据
        """
        if self.connection_status != "connected":
            raise Exception("未连接到Hermes系统")

        # 生成查询消息
        query = self.protocol.generate_query(query_type, data)
        print(f"📤 发送查询: {query_type}")

        # 模拟网络延迟和响应
        time.sleep(0.3)

        # 生成模拟响应
        response_data = self._generate_simulation_response(query_type, data)

        print("📥 接收响应")

        return response_data

    def send_command(self, command_type: str, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送命令并接收响应

        Args:
            command_type: 命令类型
            command: 命令名称
            params: 命令参数

        Returns:
            响应数据
        """
        if self.connection_status != "connected":
            raise Exception("未连接到Hermes系统")

        command_message = self.protocol.generate_command(command_type, command, params)
        print(f"📤 发送命令: {command}")

        time.sleep(0.5)

        response_data = {
            "status": "success",
            "message": f"命令 '{command}' 执行成功",
            "data": params
        }

        print("📥 命令响应成功")

        return response_data

    def _generate_simulation_response(self, query_type: str, data: Any) -> Dict[str, Any]:
        """
        生成模拟响应

        Args:
            query_type: 查询类型
            data: 查询数据

        Returns:
            模拟响应数据
        """
        responses = {
            "project_search": {
                "status": "success",
                "message": "查询成功",
                "data": [
                    {
                        "name": "Python数据分析项目",
                        "description": "使用Pandas和Matplotlib进行数据分析",
                        "stars": 1500,
                        "language": "Python"
                    },
                    {
                        "name": "Java网络应用",
                        "description": "基于Spring Boot的Web应用程序",
                        "stars": 890,
                        "language": "Java"
                    }
                ]
            },
            "expert_recommendation": {
                "status": "success",
                "message": "推荐成功",
                "data": [
                    {
                        "role": "Python专家",
                        "name": "Python数据分析专家",
                        "description": "在数据分析领域有5年经验"
                    },
                    {
                        "role": "Java专家",
                        "name": "Java后端开发专家",
                        "description": "在企业级应用开发有8年经验"
                    }
                ]
            },
            "knowledge_retrieval": {
                "status": "success",
                "message": "知识检索成功",
                "data": [
                    {
                        "topic": "机器学习基础",
                        "content": "机器学习是计算机系统通过经验自动改进性能的过程",
                        "source": "Wikipedia"
                    },
                    {
                        "topic": "深度学习",
                        "content": "深度学习是机器学习的一个分支，使用神经网络进行模式识别",
                        "source": "TensorFlow文档"
                    }
                ]
            }
        }

        return responses.get(query_type, {
            "status": "unknown",
            "message": f"未知查询类型: {query_type}",
            "data": []
        })


if __name__ == "__main__":
    # 测试协议解析器
    print("🚀 测试Hermes协议解析器")

    # 创建协议解析器
    protocol = HermesProtocol()

    print("✅ 协议解析器创建成功")

    # 测试消息生成
    print("\n📝 测试消息生成:")

    query = protocol.generate_query("project_search", {"keyword": "python"})
    print("查询消息:")
    print(query)

    response = protocol.generate_response("req_12345", {"result": "success"})
    print("\n响应消息:")
    print(response)

    command = protocol.generate_command("project_analysis", "analyze_project",
                                       {"project_id": "123"})
    print("\n命令消息:")
    print(command)

    event = protocol.generate_event("system_status", {"status": "running"})
    print("\n事件消息:")
    print(event)

    error = protocol.generate_error("req_12345", "NOT_FOUND", "项目未找到")
    print("\n错误消息:")
    print(error)

    print("\n✅ 协议解析器测试完成")

    # 测试接口
    print("\n🔌 测试Hermes接口:")

    interface = HermesInterface(protocol)
    interface.connect("http://localhost:8080")

    print("\n📤 测试查询功能:")
    search_result = interface.send_query("project_search", {"keyword": "python"})
    print(search_result)

    print("\n👨‍💼 测试专家推荐:")
    experts = interface.send_query("expert_recommendation", {"skill": "python"})
    print(experts)

    print("\n📚 测试知识检索:")
    knowledge = interface.send_query("knowledge_retrieval", {"topic": "机器学习"})
    print(knowledge)

    print("\n🎯 测试命令功能:")
    command_result = interface.send_command("analysis", "analyze_project", {"id": "123"})
    print(command_result)

    interface.disconnect()

    print("\n✅ 所有测试完成！")