# AI Agent智能体集成使用指南

本项目支持与主流AI Agent平台集成，让AI助手能够与更多的智能体进行交互，提供更丰富的学习支持。

## 🚀 支持的AI Agent平台

### 1. OpenAI (GPT系列)
- **API地址**: https://api.openai.com/v1/chat/completions
- **支持模型**: gpt-3.5-turbo, gpt-4
- **主要特点**: 自然语言处理能力强，支持复杂对话

### 2. Anthropic (Claude)
- **API地址**: https://api.anthropic.com/v1/messages
- **支持模型**: claude-3-sonnet, claude-3-opus
- **主要特点**: 长文本处理和逻辑推理能力强

### 3. 百度 (文心一言)
- **API地址**: https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions
- **支持模型**: ernie-4o, ernie-3.5
- **主要特点**: 中文处理能力强，本土化支持好

### 4. 阿里云 (通义千问)
- **API地址**: https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
- **支持模型**: qwen-turbo, qwen-plus
- **主要特点**: 高性能，响应速度快

## 📋 配置说明

### 快速配置

#### 方法1: 使用命令行配置

```python
from ai_agent_adapter import AIAgentAdapter

# 创建适配器实例
adapter = AIAgentAdapter()

# 配置OpenAI
adapter.update_agent_config(
    platform="openai",
    api_key="your-openai-api-key"
)

# 配置Claude
adapter.update_agent_config(
    platform="claude",
    api_key="your-claude-api-key"
)

# 配置百度文心一言
adapter.update_agent_config(
    platform="baidu",
    api_key="your-baidu-api-key"
)

# 配置阿里云通义千问
adapter.update_agent_config(
    platform="aliyun",
    api_key="your-aliyun-api-key"
)
```

#### 方法2: 手动编辑配置文件

编辑 `data/ai_agent_config.json` 文件：

```json
{
  "platform": "openai",
  "api_key": "your-api-key-here",
  "base_url": "",
  "agent_id": "",
  "timeout": 30,
  "retries": 3
}
```

### 配置参数说明

| 参数名 | 说明 | 可选值 | 默认值 |
|--------|------|--------|--------|
| platform | 平台名称 | openai, claude, baidu, aliyun, default | default |
| api_key | API密钥 | 字符串 | "" |
| base_url | API地址 | URL字符串 | 平台默认地址 |
| agent_id | 智能体ID | 字符串 | "" |
| timeout | 请求超时时间(秒) | 整数 | 30 |
| retries | 重试次数 | 整数 | 3 |

## 🎯 使用方法

### 基础使用

```python
from ai_agent_adapter import AIAgentAdapter

# 创建AI Agent适配器
adapter = AIAgentAdapter("openai")

# 检查配置状态
print("配置状态:", adapter.is_agent_available())

# 发送消息
response = adapter.send_message("你好，请介绍一下机器学习的基本概念")
if response:
    print("AI响应:", response)

# 获取学习建议
response = adapter.get_agent_response("我需要学习Python数据分析项目")
if response:
    print("学习建议:", response)
```

### 高级功能

#### 1. 命令执行

```python
# 执行项目分析命令
result = adapter.execute_agent_command("analyze_code")

# 检查系统漏洞
result = adapter.execute_agent_command("check_vulnerability")

# 优化系统
result = adapter.execute_agent_command("optimize_system")

# 搜索AI知识
result = adapter.execute_agent_command("search_knowledge")

# 生成学习建议
result = adapter.execute_agent_command("generate_suggestion")

# 更新知识库
result = adapter.execute_agent_command("update_knowledge")
```

#### 2. 知识库管理

```python
# 更新知识库
knowledge_items = [
    "Python数据分析项目",
    "机器学习算法",
    "网络安全最佳实践",
    "大语言模型最新进展"
]

success = adapter.update_agent_knowledge(knowledge_items)
print("更新知识库:", success)
```

#### 3. 上下文感知

AI Agent适配器会自动从项目数据中获取上下文信息：

```python
# 获取用户状态
user_context = adapter._prepare_context()
print("用户上下文:", user_context)
```

## 🔍 故障排除

### 1. API密钥未配置

**错误信息**: `⚠️  AI Agent不可用，请先配置API密钥`

**解决方法**:
```python
# 检查配置文件
with open("data/ai_agent_config.json", "r") as f:
    config = json.load(f)
    print("API密钥配置:", config["api_key"])

# 重新配置
from ai_agent_adapter import AIAgentAdapter
adapter = AIAgentAdapter()
adapter.update_agent_config(
    platform="openai",
    api_key="your-api-key-here"
)
```

### 2. 请求超时

**错误信息**: `TimeoutError`

**解决方法**:
```python
# 增加超时时间
adapter.update_agent_config(
    platform="openai",
    api_key="your-api-key",
    timeout=60,
    retries=5
)
```

### 3. API访问限制

**错误信息**: `RateLimitError`

**解决方法**:
- 检查API使用额度
- 调整请求频率
- 使用API限流机制

### 4. 网络连接问题

**错误信息**: `ConnectionError`

**解决方法**:
- 检查网络连接
- 验证API访问地址
- 检查防火墙设置

## 📈 性能优化

### 1. 批量处理

```python
# 批量发送消息
messages = [
    "Python数据分析学习路径",
    "机器学习算法介绍",
    "数据可视化工具推荐"
]

results = []
for msg in messages:
    response = adapter.send_message(msg)
    results.append(response)
```

### 2. 响应缓存

```python
# 实现响应缓存
import time

class AIAgentWithCache(AIAgentAdapter):
    def __init__(self, platform="default"):
        super().__init__(platform)
        self.response_cache = {}
        
    def send_message(self, message, context=None):
        cache_key = f"{self.platform}:{message}"
        
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]
        
        response = super().send_message(message, context)
        
        if response:
            self.response_cache[cache_key] = response
            
        return response
```

### 3. 异步调用

```python
# 异步处理
import asyncio

async def send_message_async(adapter, message):
    return await asyncio.get_event_loop().run_in_executor(
        None, adapter.send_message, message
    )

# 使用方法
async def main():
    adapter = AIAgentAdapter("openai")
    results = await asyncio.gather(
        send_message_async(adapter, "问题1"),
        send_message_async(adapter, "问题2"),
        send_message_async(adapter, "问题3")
    )
    print("结果:", results)
```

## 📞 支持的命令类型

| 命令名 | 说明 | 功能 |
|--------|------|------|
| analyze_code | 分析代码质量 | 检查项目代码问题 |
| check_vulnerability | 检查系统漏洞 | 扫描安全问题 |
| optimize_system | 优化系统性能 | 提供系统优化建议 |
| search_knowledge | 搜索AI知识 | 获取最新AI信息 |
| generate_suggestion | 生成学习建议 | 根据学习进度推荐 |
| update_knowledge | 更新知识库 | 维护知识体系 |

## 🎯 最佳实践

### 1. 多平台切换

```python
# 根据配置动态选择平台
platform = config.get("platform", "default")
adapter = AIAgentAdapter(platform)
```

### 2. 容错机制

```python
# 实现容错逻辑
def robust_ai_communication(adapter, message):
    try:
        response = adapter.send_message(message)
        if response:
            return response
    except Exception as e:
        print(f"AI通信失败: {e}")
    
    # 降级方案
    return f"无法获取AI响应。问题: {message}"
```

### 3. 性能监控

```python
# 监控AI Agent性能
import time

start_time = time.time()
response = adapter.send_message("学习建议")
duration = time.time() - start_time

print(f"响应时间: {duration:.2f}秒")

# 记录性能数据
with open("ai_agent_performance.log", "a") as f:
    f.write(f"{time.time()},{duration:.2f},{len(response)}\n")
```

## 🚀 快速开始脚本

创建 `start_ai_agent.py`：

```python
#!/usr/bin/env python3
"""AI Agent集成测试脚本"""

from ai_agent_adapter import AIAgentAdapter

def main():
    print("🚀 启动AI Agent集成测试")
    print("=" * 60)
    
    # 创建AI Agent适配器
    adapter = AIAgentAdapter("default")
    
    # 显示配置状态
    print("配置状态:")
    stats = adapter.get_agent_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
        
    # 测试基本功能
    print("\n📝 测试基本功能:")
    
    # 1. 检查配置状态
    if adapter.is_agent_available():
        print("✅ API密钥配置完成")
    else:
        print("⚠️  API密钥未配置，请检查data/ai_agent_config.json")
    
    # 2. 发送测试消息
    print("\n📩 发送测试消息:")
    response = adapter.send_message("你好，请介绍一下自己")
    
    if response:
        print("✅ AI响应:")
        print(f"   {response}")
    else:
        print("⚠️  未收到AI响应")
    
    # 3. 测试命令执行
    print("\n🎯 测试命令执行:")
    command_result = adapter.execute_agent_command("generate_suggestion")
    
    if command_result:
        print("✅ 命令执行成功")
        print(f"   结果: {command_result}")
    else:
        print("⚠️  命令执行失败")
    
    print("\n🎉 测试完成!")
    
    return 0

if __name__ == "__main__":
    main()
```

运行脚本：

```bash
python start_ai_agent.py
```

## 📚 资源链接

### API文档
- [OpenAI API](https://platform.openai.com/docs/introduction)
- [Claude API](https://docs.anthropic.com/claude/reference/)
- [百度AI开放平台](https://ai.baidu.com/)
- [阿里云AI服务](https://www.aliyun.com/product/ai/)

### 学习资源
- [AI Agent架构设计](https://developer.nvidia.com/blog/ai-agent-architecture/)
- [自然语言处理](https://huggingface.co/learn)
- [深度学习教程](https://www.tensorflow.org/tutorials)

### 社区支持
- [GitHub项目](https://github.com/yourusername/github-learning)
- [Discord社区](https://discord.gg/your-community-link)
- [Stack Overflow](https://stackoverflow.com/tags/ai-agent)

## 📄 许可证

AI Agent集成组件遵循项目的GNU General Public License v3.0 (GPLv3) 许可证。

---

**说明**: 不同AI平台可能有API使用限制和费用计算方式，请在使用前查阅相应平台的文档和条款。
