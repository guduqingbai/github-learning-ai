# 贾维斯式主动沟通AI系统

[![GitHub license](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://github.com/guduqingbai/github-learning-ai/blob/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/guduqingbai/github-learning-ai/blob/master/CONTRIBUTING.md)

## 项目概述

贾维斯式主动沟通AI系统是一个智能化学习助手，能够主动分析用户学习状态、提供个性化建议，并在用户离线时自动进行自我学习和系统完善。该系统借鉴了钢铁侠中贾维斯的主动沟通模式，旨在帮助用户高效管理学习任务和持续提升专业技能。

## 核心功能特性

### 1. 主动沟通机制
- **智能状态感知**：通过时间分析判断用户在线/离线状态（5分钟内有交互视为在线）
- **个性化建议**：根据学习进度提供定制化学习方向和任务
- **沟通时机优化**：基于项目完成数量和学习时长智能判断沟通时机
- **响应处理系统**：智能解析用户响应并执行相应的学习任务

### 2. 自我学习系统
- **漏洞扫描与修复**：定期检查系统漏洞和代码质量问题，新增`fix_vulnerabilities()`方法
- **系统安全修复**：自动检测并修复权限问题、硬编码密码和SQL注入风险
- **全球知识获取**：从11个全球AI知识平台获取实时信息
- **代码分析与优化**：自动化解析项目代码并提供改进建议
- **系统自我完善**：根据学习成果持续优化系统功能

### 3. 学习管理系统
- **进度追踪**：详细记录学习成果和沟通历史
- **项目管理**：智能识别和管理学习项目
- **知识更新**：每次学习都会获取全球最新AI知识
- **效果评估**：分析学习效果并提供改进建议

## 项目结构

```
github-learning/
├── data/                              # 数据存储目录
│   ├── active_state.json             # 系统状态文件
│   ├── learning_progress.json        # 学习进度记录
│   ├── jarvis_monitor_state.json     # 贾维斯系统状态
│   └── conversations.jsonl           # 沟通历史记录
├── 📄 jarvis_monitor_noninteractive.py  # 主动沟通系统
├── 📄 active_communication.py        # 沟通机制实现
├── 📄 expert_system.py               # 专家系统
├── 📄 ai_agent_adapter.py            # AI代理适配器
├── 📄 knowledge_base.py              # 知识库管理
├── 📄 README.md                      # 项目说明
├── 📄 CONTRIBUTING.md                # 贡献指南
├── 📄 USAGE.md                       # 使用说明
├── 📄 requirements.txt               # 依赖包
└── 📄 LICENSE                        # GPLv3许可证
```

## 安装与配置

### 环境要求
- Python 3.8+
- 稳定的网络连接

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/guduqingbai/github-learning-ai.git
   cd github-learning-ai
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **初始化系统**
   ```bash
   python jarvis_monitor_noninteractive.py
   ```

## 使用指南

### 基本使用流程

```bash
# 启动主动沟通系统
python jarvis_monitor_noninteractive.py

# 启动主动沟通循环（带交互）
python active_communication.py

# 查看学习进度
python learning_progress.py --view

# 执行系统安全漏洞修复
python -c "from self_learning_system import SelfLearningSystem; system = SelfLearningSystem(); system.fix_vulnerabilities()"

# 运行完整自我学习周期
python -c "from self_learning_system import SelfLearningSystem; system = SelfLearningSystem(); system.run_self_learning_cycle()"
```

## 技术栈

- **Python 3.8+**：主要开发语言
- **JSON**：数据存储格式
- **Git**：版本控制

## 许可证

本项目采用 **GNU General Public License v3.0 (GPLv3)** 许可证，详情请参考 [LICENSE](LICENSE) 文件。

### 许可证特点

- **强制开源**：任何使用本项目代码的产品或服务必须开源
- **专利保护**：提供专利授权，防止专利诉讼
- **升级保护**：允许自动升级到更高版本的GPL许可证
- **反锁定条款**：防止硬件制造商锁定软件

## 联系方式

- **问题反馈**：通过 [GitHub Issues](https://github.com/guduqingbai/github-learning-ai/issues) 报告问题
- **功能请求**：通过 [GitHub Discussions](https://github.com/guduqingbai/github-learning-ai/discussions) 提出建议
- **邮件联系**：3536778780@qq.com

## 项目状态

**项目已完成** - 包含主动沟通、自我学习和专家系统功能
**系统优化完成** - 新增系统安全漏洞修复功能
**文档完善完成** - 提供专业的项目文档
**学习进度** - 12个项目完成，330分钟学习时间，高级阶段
**功能特性** - 主动沟通、情感识别、关系管理、解释型AI、个性化学习
