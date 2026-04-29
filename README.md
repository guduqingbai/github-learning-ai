# 学习数据分析与优化系统

[![GitHub license](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://github.com/guduqingbai/github-learning-ai/blob/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/guduqingbai/github-learning-ai/blob/master/CONTRIBUTING.md)

## 项目概述

学习数据分析与优化系统是一个**基于数据驱动的学习辅助工具**，专注于收集、分析和优化学习过程。该系统能够：
- 收集和分析学习数据
- 追踪学习进度和效果
- 评估学习效率和质量
- 提供个性化学习建议
- 自动化学习任务执行

## 核心功能特性

### 1. 数据分析系统
- **学习进度追踪**：记录和分析学习活动
- **效率评估**：分析学习效率和质量
- **数据可视化**：提供学习数据的可视化展示
- **统计分析**：对学习数据进行深度统计

### 2. 优化建议系统
- **学习策略优化**：基于数据分析提供优化建议
- **任务自动化**：定时执行学习任务
- **进度提醒**：提供学习进度和目标提醒
- **效率改进**：分析学习模式并提供改进建议

### 3. 浏览器集成系统
- **Tabbit浏览器集成**：与Tabbit浏览器深度集成
- **学习数据收集**：收集浏览器学习数据
- **内容分析**：分析浏览器内容与学习的相关性
- **浏览器同步**：同步浏览器状态与学习系统

### 4. 认知架构系统
- **认知循环**：实现完整的感知→推理→决策→学习循环
- **感知系统**：类似人类的学习数据和外部信息感知
- **推理系统**：基于认知科学的情境推理和决策
- **学习系统**：从经验中学习和优化的能力

### 5. 持续学习系统
- **自我学习**：自动查找、学习和获取新知识
- **内容评估**：评估学习内容的价值和重要性
- **学习优化**：根据学习状态调整学习策略
- **知识积累**：持续构建和扩展知识库

### 6. 主动沟通系统
- **情感识别**：根据学习状态判断用户情感（积极/中性/消极）
- **关系管理**：评估与用户的关系质量并提供优化建议
- **主动沟通**：自我发现学习机会并主动与用户沟通
- **响应处理**：智能处理用户的各种响应类型

### 7. 系统管理系统
- **漏洞扫描**：定期检查系统安全漏洞
- **代码质量分析**：自动化代码质量检查
- **系统监控**：实时监控系统运行状态
- **维护管理**：系统维护和优化

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
├── 📄 browser_integration.py         # 浏览器集成模块
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

# 启动持续学习系统（自我学习和知识获取）
python continuous_learning.py

# 测试认知架构系统
python -c "from cognitive_architecture import test_cognitive_architecture; test_cognitive_architecture()"

# 测试持续学习系统
python -c "from continuous_learning import test_continuous_learning; test_continuous_learning()"

# 浏览器集成使用
python browser_integration.py              # 测试浏览器集成模块
python -c "from browser_integration import BrowserIntegration; bi = BrowserIntegration(); bi.get_browser_integration_status()"

# 启用Tabbit浏览器集成
python -c "from browser_integration import BrowserIntegration; bi = BrowserIntegration(); result, message = bi.enable_browser_integration('tabbit'); print(f'{result}: {message}')"

# 启动学习内容分析
python -c "from browser_integration import BrowserIntegration; bi = BrowserIntegration(); result, message = bi.start_learning_content_analysis(); print(f'{result}: {message}')"
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
- **邮件联系**：github@example.com

## 项目状态

**项目已完成** - 包含数据分析、优化建议和系统管理功能
**系统优化完成** - 新增学习数据分析和优化功能
**浏览器集成完成** - 新增Tabbit浏览器集成功能
**文档完善完成** - 提供专业的项目文档
**学习进度** - 54个主题，12300分钟学习时间，高效学习阶段
**功能特性** - 数据收集、分析、优化建议、任务自动化、浏览器集成
