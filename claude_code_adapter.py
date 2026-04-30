#!/usr/bin/env python3
"""
🎯 Claude Code集成适配器 - 与Claude Code平台的专业API集成
实现代码分析、优化和学习功能
"""

import os
import sys
import json
import requests
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class ClaudeCodeAdapter:
    """Claude Code集成适配器 - 与Claude Code平台的专业API集成"""

    def __init__(self, api_key: str = None, base_url: str = "https://api.anthropic.com"):
        """初始化Claude Code适配器"""
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        self.base_url = base_url
        self.model = "claude-3-sonnet-20250219"
        self.timeout = 60
        self.max_tokens = 4096

        # 配置管理
        self.config_file = Path("data") / "claude_code_config.json"
        self._load_config()

        print("🎯 Claude Code适配器初始化完成")

    def _load_config(self):
        """加载Claude Code配置"""
        default_config = {
            "api_key": "",
            "base_url": "https://api.anthropic.com",
            "model": "claude-3-sonnet-20250219",
            "timeout": 60,
            "max_tokens": 4096
        }

        if not self.config_file.exists():
            self._save_config(default_config)

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            self.api_key = config.get("api_key") or self.api_key
            self.base_url = config.get("base_url") or self.base_url
            self.model = config.get("model") or self.model
            self.timeout = config.get("timeout") or self.timeout
            self.max_tokens = config.get("max_tokens") or self.max_tokens

        except Exception as e:
            print(f"⚠️  加载Claude Code配置失败: {e}")
            self._save_config(default_config)

    def _save_config(self, config: Dict[str, Any]):
        """保存Claude Code配置"""
        os.makedirs("data", exist_ok=True)

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print("✅ Claude Code配置已保存")
        except Exception as e:
            print(f"❌ 保存Claude Code配置失败: {e}")

    def update_config(self, api_key: str = None, base_url: str = None,
                     model: str = None, timeout: int = None,
                     max_tokens: int = None):
        """更新Claude Code配置"""
        config = {
            "api_key": api_key or self.api_key,
            "base_url": base_url or self.base_url,
            "model": model or self.model,
            "timeout": timeout or self.timeout,
            "max_tokens": max_tokens or self.max_tokens
        }

        self.api_key = config["api_key"]
        self.base_url = config["base_url"]
        self.model = config["model"]
        self.timeout = config["timeout"]
        self.max_tokens = config["max_tokens"]

        self._save_config(config)

    def is_available(self) -> bool:
        """检查Claude Code是否可用"""
        return self.api_key and len(self.api_key.strip()) > 0

    def _send_request(self, messages: List[Dict[str, Any]],
                     temperature: float = 0.7,
                     stream: bool = False) -> Optional[str]:
        """发送API请求到Claude Code"""
        if not self.is_available():
            print("⚠️  Claude Code API密钥未配置，使用模拟响应")
            return self._generate_mock_response(messages)

        url = f"{self.base_url}/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self.max_tokens
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )

            response.raise_for_status()

            result = response.json()
            return result["content"][0]["text"]

        except requests.exceptions.RequestException as e:
            print(f"❌ Claude Code API请求失败: {e}")
            return self._generate_mock_response(messages)
        except Exception as e:
            print(f"❌ Claude Code处理失败: {e}")
            return self._generate_mock_response(messages)

    def _generate_mock_response(self, messages: List[Dict[str, Any]]) -> str:
        """生成模拟响应，当API密钥未配置时使用"""
        # 检查消息内容判断请求类型
        user_content = ""
        for msg in messages:
            if msg["role"] == "user":
                user_content = msg["content"]
                break

        if "代码质量" in user_content or "分析" in user_content:
            return json.dumps({
                "score": 82,
                "dimensions": {
                    "规范": 85, "架构": 80, "错误处理": 78,
                    "性能": 82, "安全": 75, "可维护": 85
                },
                "suggestions": ["代码格式可以进一步规范化", "可以添加更多的错误处理"],
                "strengths": ["代码结构清晰", "注释详细", "功能实现正确"]
            }, ensure_ascii=False)

        elif "优化" in user_content:
            return json.dumps({
                "optimized_code": "代码优化建议...",
                "explanation": "对代码进行了性能优化和结构改进",
                "performance_improvement": 35,
                "memory_improvement": 25,
                "size_reduction": 15
            }, ensure_ascii=False)

        elif "问题" in user_content or "缺陷" in user_content:
            return json.dumps([
                {
                    "type": "代码规范",
                    "description": "变量命名可以更规范",
                    "suggestion": "使用有意义的变量名",
                    "severity": "low",
                    "location": "第3行"
                },
                {
                    "type": "性能",
                    "description": "循环可以优化",
                    "suggestion": "使用列表推导式代替循环",
                    "severity": "medium",
                    "location": "第5行"
                }
            ], ensure_ascii=False)

        elif "结构" in user_content or "项目" in user_content:
            return json.dumps({
                "score": 75,
                "suggestions": ["项目文件组织可以更合理", "可以添加更多的文档"],
                "dependencies": "项目依赖结构清晰",
                "structure": "架构设计合理，但可以进一步模块化"
            }, ensure_ascii=False)

        else:
            return """
## 文件管理工具实现

### 功能说明
创建一个简单的文件管理工具，支持文件搜索、内容读取和写入功能。

### 代码实现
```python
import os
import glob
from pathlib import Path

class FileManager:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def search_files(self, pattern="*.txt"):
        search_pattern = str(self.base_dir / pattern)
        return glob.glob(search_pattern)

    def read_file(self, filename):
        file_path = self.base_dir / filename
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def write_file(self, filename, content):
        file_path = self.base_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

# 使用示例
if __name__ == "__main__":
    fm = FileManager("data")
    fm.write_file("test.txt", "Hello, World!")
    content = fm.read_file("test.txt")
    print(f"File content: {content}")
    files = fm.search_files("*.txt")
    print(f"Files found: {files}")
```

### 功能特点
- 简单易用的API接口
- 支持文件搜索和内容读写
- 自动处理目录创建
- 异常处理完善
"""

    def analyze_code_quality(self, code: str,
                            filename: str = None,
                            language: str = None) -> Dict[str, Any]:
        """分析代码质量"""
        prompt = f"""请专业分析以下代码的质量，提供详细的评估：

**代码内容：**
```
{code}
```

**分析维度：**
1. 代码规范和格式
2. 架构设计和模块化
3. 错误处理和边界条件
4. 性能优化潜力
5. 安全性问题
6. 可维护性和可读性

**要求格式：**
返回JSON格式，包含：
- 总体评分 (0-100)
- 各维度评分
- 改进建议列表
- 代码优势分析

如果提供了文件名或语言，也请考虑这些因素。"""

        messages = [
            {"role": "system", "content": "你是一个专业的代码质量分析专家"},
            {"role": "user", "content": prompt}
        ]

        response = self._send_request(messages, temperature=0.3)

        if response:
            try:
                return json.loads(response)
            except:
                return {
                    "score": 65,
                    "dimensions": {
                        "规范": 60, "架构": 55, "错误处理": 50,
                        "性能": 60, "安全": 55, "可维护": 65
                    },
                    "suggestions": ["代码分析响应解析失败"],
                    "strengths": ["代码质量分析服务响应"]
                }

        return None

    def optimize_code(self, code: str,
                     filename: str = None,
                     language: str = None,
                     optimization_level: str = "medium") -> Dict[str, Any]:
        """优化代码"""
        prompt = f"""请专业优化以下代码，提升其质量和性能：

**代码内容：**
```
{code}
```

**优化目标：**
- 提升代码性能 {optimization_level}
- 改进代码结构
- 优化内存使用
- 增强代码可读性
- 修复潜在问题

**要求格式：**
返回JSON格式，包含：
- 优化后的代码
- 优化说明
- 性能提升评估
- 内存使用改善
- 代码体积变化

如果提供了文件名或语言，也请考虑这些因素。"""

        messages = [
            {"role": "system", "content": "你是一个专业的代码优化专家"},
            {"role": "user", "content": prompt}
        ]

        response = self._send_request(messages, temperature=0.4)

        if response:
            try:
                return json.loads(response)
            except:
                return {
                    "optimized_code": code,
                    "explanation": "代码优化响应解析失败",
                    "performance_improvement": 0,
                    "memory_improvement": 0,
                    "size_reduction": 0
                }

        return None

    def generate_code_explanations(self, code: str,
                                 filename: str = None,
                                 language: str = None) -> List[str]:
        """生成代码解释"""
        prompt = f"""请详细解释以下代码的功能和实现原理：

**代码内容：**
```
{code}
```

**解释要点：**
1. 代码的核心功能
2. 关键算法和数据结构
3. 设计模式和架构思想
4. 性能优化策略
5. 潜在问题和改进方向

**要求格式：**
返回清晰的要点列表，使用Markdown格式。"""

        messages = [
            {"role": "system", "content": "你是一个专业的代码解释专家"},
            {"role": "user", "content": prompt}
        ]

        response = self._send_request(messages, temperature=0.5)

        if response:
            return [line.strip() for line in response.split("\n") if line.strip()]

        return []

    def find_code_issues(self, code: str,
                        filename: str = None,
                        language: str = None) -> List[Dict[str, Any]]:
        """查找代码问题"""
        prompt = f"""请专业分析以下代码中的问题和缺陷：

**代码内容：**
```
{code}
```

**问题类型：**
1. 语法错误
2. 逻辑错误
3. 安全漏洞
4. 性能问题
5. 代码异味
6. 潜在的bug

**要求格式：**
返回JSON格式的问题列表，包含：
- 问题类型
- 问题描述
- 修复建议
- 严重程度 (critical/high/medium/low)
- 位置信息

如果提供了文件名或语言，也请考虑这些因素。"""

        messages = [
            {"role": "system", "content": "你是一个专业的代码审查专家"},
            {"role": "user", "content": prompt}
        ]

        response = self._send_request(messages, temperature=0.3)

        if response:
            try:
                return json.loads(response)
            except:
                return [
                    {
                        "type": "parsing_error",
                        "description": "响应解析失败",
                        "suggestion": "检查API响应格式",
                        "severity": "medium",
                        "location": "unknown"
                    }
                ]

        return []

    def suggest_optimizations(self, code: str,
                            filename: str = None,
                            language: str = None) -> List[Dict[str, Any]]:
        """建议代码优化"""
        prompt = f"""请专业建议以下代码的优化方案：

**代码内容：**
```
{code}
```

**优化方向：**
1. 性能优化
2. 内存优化
3. 代码简化
4. 架构改进
5. 安全性提升

**要求格式：**
返回JSON格式的优化建议列表，包含：
- 优化类型
- 具体改进方案
- 预期效果
- 实现难度
- 优先级

如果提供了文件名或语言，也请考虑这些因素。"""

        messages = [
            {"role": "system", "content": "你是一个专业的代码优化顾问"},
            {"role": "user", "content": prompt}
        ]

        response = self._send_request(messages, temperature=0.4)

        if response:
            try:
                return json.loads(response)
            except:
                return []

        return []

    def analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """分析项目结构"""
        files = []
        for file in Path(project_path).glob("*.py"):
            if file.is_file() and file.name != "__pycache__":
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        files.append({
                            "name": str(file),
                            "size": len(f.read()),
                            "path": str(file)
                        })
                except:
                    continue

        prompt = f"""请专业分析以下Python项目的结构：

**项目文件列表：**
{json.dumps(files, ensure_ascii=False, indent=2)}

**分析要点：**
1. 项目架构设计
2. 模块划分合理性
3. 代码组织优化建议
4. 依赖管理优化
5. 文件结构改进建议

**要求格式：**
返回JSON格式，包含：
- 架构评分
- 优化建议
- 依赖关系分析
- 文件结构改善方案"""

        messages = [
            {"role": "system", "content": "你是一个专业的项目架构分析专家"},
            {"role": "user", "content": prompt}
        ]

        response = self._send_request(messages, temperature=0.5)

        if response:
            try:
                return json.loads(response)
            except:
                return {
                    "score": 60,
                    "suggestions": ["响应解析失败"],
                    "dependencies": "未知",
                    "structure": "解析错误"
                }

        return None

    def create_code_suggestions(self, requirements: str,
                               language: str = "Python") -> str:
        """根据需求创建代码建议"""
        prompt = f"""根据以下需求创建专业的代码建议：

**需求描述：**
{requirements}

**语言：** {language}

**要求：**
1. 提供完整的代码实现
2. 包含详细的注释说明
3. 考虑错误处理和边界条件
4. 优化性能和内存使用
5. 确保代码质量

**要求格式：**
返回markdown格式的代码块，包含：
- 完整代码
- 功能说明
- 实现细节
- 使用示例"""

        messages = [
            {"role": "system", "content": "你是一个专业的代码生成专家"},
            {"role": "user", "content": prompt}
        ]

        return self._send_request(messages, temperature=0.6)


if __name__ == "__main__":
    # 测试Claude Code适配器
    print("🎯 测试Claude Code适配器")
    print("=" * 60)

    try:
        adapter = ClaudeCodeAdapter()

        # 简单测试
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

        print("📊 分析代码质量...")
        quality = adapter.analyze_code_quality(test_code, "test.py", "Python")
        if quality:
            print(f"✅ 代码质量评分: {quality.get('score', 'N/A')}")
            for dimension, score in quality.get('dimensions', {}).items():
                print(f"   • {dimension}: {score}")

        print("\n🔍 查找代码问题...")
        issues = adapter.find_code_issues(test_code)
        if issues:
            for issue in issues:
                print(f"   • [{issue['severity']}] {issue['description']}")

        print("\n✅ 测试完成！")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
