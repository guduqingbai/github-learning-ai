# 📦 项目安装与配置

本项目是一个类似钢铁侠贾维斯的主动沟通AI学习系统，包含多个核心功能模块。

## 🚀 快速开始

### 1. 系统要求

- Python 3.7+
- 操作系统: Windows 10/11, macOS, Linux
- 网络连接（用于访问外部API）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行项目

#### 选项1: 直接运行贾维斯主动沟通系统

```bash
python jarvis_monitor_noninteractive.py
```

#### 选项2: 运行完整的Hermes系统

```bash
python hermes_integration.py
```

#### 选项3: 运行演示脚本

```bash
python demo.py
```

## ⚙️ 配置说明

### 1. 系统配置

项目配置文件位于 `data/` 目录下：

#### active_state.json
```json
{
    "last_interaction": "2026-04-28T20:15:30.123456",
    "projects_completed": 0,
    "communication_count": 0,
    "response_count": 0,
    "learning_stage": "beginner"
}
```

#### learning_progress.json
```json
{
    "total_study_time": 0,
    "projects_studied": [],
    "knowledge_points": [],
    "learning_effectiveness": 0.85,
    "communication_effectiveness": 0.92
}
```

### 2. AI Agent配置

配置文件位于 `data/ai_agent_config.json`：

```json
{
    "platform": "default",
    "api_key": "",
    "base_url": "",
    "agent_id": "",
    "timeout": 30,
    "retries": 3
}
```

#### 配置说明

| 参数 | 说明 | 可选值 |
|------|------|--------|
| platform | AI Agent平台 | openai, claude, baidu, aliyun, default |
| api_key | API密钥 | 字符串 |
| base_url | API基础地址 | URL |
| agent_id | 智能体ID | 字符串 |
| timeout | 请求超时时间(秒) | 整数 |
| retries | 重试次数 | 整数 |

## 🎯 功能模块

### 1. 贾维斯主动沟通系统 (`jarvis_monitor_noninteractive.py`)

- **用户状态识别**: 判断用户是否可用
- **智能沟通**: 根据用户状态主动发起沟通
- **自我学习**: 用户不在线时自动学习
- **进度追踪**: 记录学习进度和沟通历史

### 2. Hermes系统集成 (`hermes_integration.py`)

- **专家系统**: 8个专家角色，6个知识条目
- **知识管理**: 知识库检索和学习
- **项目分析**: 自动项目分析和推荐
- **协议支持**: OpenClaw/Hermes协议

### 3. AI Agent适配器 (`ai_agent_adapter.py`)

- **多平台支持**: OpenAI、Claude、百度、阿里云
- **统一接口**: 不同AI平台的兼容层
- **配置管理**: 自动配置加载和更新
- **容错处理**: 请求失败时的降级处理

### 4. 自我学习系统 (`self_learning_system.py`)

- **漏洞检查**: 系统安全检查
- **代码分析**: 代码质量评估
- **网络学习**: 从全球AI知识平台获取信息
- **系统优化**: 自动优化和改进

## 🔧 开发说明

### 1. 项目结构

```
github-learning/
├── 📁 data/                      # 数据存储目录
├── 📁 adaptive_ai_projects/      # 学习项目
├── 📁 hermes_analysis/           # Hermes架构分析
├── 📄 jarvis_monitor_noninteractive.py    # 贾维斯系统
├── 📄 hermes_integration.py      # Hermes系统
├── 📄 ai_agent_adapter.py        # AI Agent适配器
├── 📄 self_learning_system.py    # 自我学习系统
├── 📄 demo.py                    # 项目演示
└── 📄 requirements.txt           # 依赖包
```

### 2. 开发环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行项目
python demo.py
```

### 3. 代码规范

- 遵循PEP 8编码规范
- 使用docstrings注释函数
- 异常处理和日志记录
- 单元测试（未完成）

## 🐛 故障排除

### 1. 常见问题

#### 问题: AI Agent不可用
**解决方案**: 检查 `data/ai_agent_config.json` 文件中的API密钥配置。

#### 问题: 无法连接到Hermes系统
**解决方案**: 确保系统配置正确，检查网络连接。

#### 问题: 学习任务执行失败
**解决方案**: 检查 `data/` 目录下的状态文件是否正确。

### 2. 日志和调试

项目使用标准输出进行调试信息输出，重要信息会打印到控制台。

## 📈 性能优化

### 1. 系统优化建议

- **减少网络请求**: 使用本地缓存
- **优化学习任务**: 减少不必要的知识获取
- **配置调整**: 根据实际需求调整超时和重试参数

### 2. 扩展功能

项目架构支持以下扩展：

1. **添加新AI平台**
2. **扩展专家系统**
3. **增强自我学习能力**
4. **优化沟通策略**

## 📚 相关资源

- **项目文档**: README.md, USAGE.md, CONTRIBUTING.md
- **API文档**: AI_AGENT_USAGE.md
- **架构分析**: hermes_architecture_analysis.md

## 📞 支持与反馈

如有问题或建议，请通过以下方式联系：

1. 创建GitHub Issue
2. 提交Pull Request
3. 发送邮件至项目邮箱

---

**项目版本**: v1.0.0  
**发布日期**: 2026年4月28日  
**许可证**: MIT License
