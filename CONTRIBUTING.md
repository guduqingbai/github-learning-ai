# 贡献指南

欢迎您为项目做出贡献！我们非常欢迎各种形式的贡献，包括但不限于：

- 🐛 报告问题
- 💡 功能建议
- 📝 文档改进
- 🔧 代码修复
- ✨ 功能实现

## 📋 贡献流程

### 1. 发现问题或建议

如果您发现问题或有功能建议，请：

1. 首先查看 [Issues](https://github.com/yourusername/github-learning/issues) 中是否已经存在类似的问题
2. 如果不存在，创建新的 Issue
3. 详细描述您的问题或建议

### 2. 准备贡献

1. Fork 项目到您的 GitHub 账户
2. 克隆 Fork 后的项目到本地
3. 创建并切换到新的分支：
   ```bash
   git clone https://github.com/yourusername/github-learning.git
   cd github-learning
   git branch feature/your-feature-name
   git checkout feature/your-feature-name
   ```

### 3. 实现功能

1. 根据您的计划实现功能
2. 确保代码符合项目的编码规范
3. 编写测试（如果需要）
4. 确保所有现有测试通过

### 4. 提交变更

1. 添加您的修改：
   ```bash
   git add .
   ```

2. 提交变更，使用有意义的提交信息：
   ```bash
   git commit -m "功能实现：添加用户状态检测功能"
   ```

### 5. 推送和 PR

1. 将您的修改推送到您的 GitHub 仓库：
   ```bash
   git remote add upstream https://github.com/yourusername/github-learning.git
   git push -u upstream feature/your-feature-name
   ```

2. 打开 Pull Request (PR)

### 6. 审核和合并

1. 我们会审查您的 PR
2. 如果有建议或修改，请根据评论进行调整
3. 当 PR 符合要求时，我们会将其合并到主分支

## 🔧 开发规范

### 编码规范

1. 使用 Python 3.6+ 语法
2. 遵循 PEP 8 编码规范
3. 使用有意义的变量和函数名
4. 添加适当的文档字符串

### 文件结构

```
github-learning/
├── 📁 data/               # 数据存储目录
├── 📄 jarvis_*.py         # 核心功能文件
├── 📄 self_learning_system.py
├── 📄 README.md           # 项目说明
├── 📄 requirements.txt    # 依赖包
└── 📄 LICENSE             # 许可证
```

### 分支管理

- `main`：主分支，生产版本
- `feature/*`：功能开发分支
- `hotfix/*`：紧急修复分支

### 提交信息格式

```
类型：描述

详细说明（可选）
```

类型说明：
- `✨ 功能`：新功能实现
- `🐛 修复`：问题修复
- `📝 文档`：文档改进
- `🔧 重构`：代码重构
- `🎨 优化`：性能优化
- `✅ 测试`：测试相关
- `🚀 发布`：版本发布

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/yourusername/github-learning.git
cd github-learning

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest

# 运行项目
python jarvis_monitor_noninteractive.py
```

## 🐛 问题报告

### 如何报告问题

1. 检查 [Issues](https://github.com/yourusername/github-learning/issues) 中是否有类似的问题
2. 使用搜索功能查找可能相关的问题
3. 如果没有找到，创建新的 Issue

### 问题描述格式

```
## 问题描述
简明描述问题所在。

## 重现步骤
1. 运行什么命令
2. 输入什么内容
3. 期望的结果
4. 实际的结果

## 系统信息
- 操作系统：Windows 10
- Python 版本：3.8.5
- 项目版本：v1.0.0

## 错误信息（可选）
```

### 可能的解决方案（可选）

如果您有解决方案的思路，可以添加在问题中。

## 📄 许可证

本项目采用 GNU General Public License v3.0 (GPLv3) 许可证，详情请参考 [LICENSE](LICENSE) 文件。

### 许可证特点
- **强制开源**：任何使用本项目代码的产品或服务必须开源
- **专利保护**：提供专利授权，防止专利诉讼
- **升级保护**：如果有更高版本的GPL许可证，允许自动升级
- **反锁定条款**：防止硬件制造商锁定软件

## 📞 联系方式

如果您有任何问题，可以通过以下方式联系我们：

- **邮件**：3536778780@qq.com
- **GitHub Issues**：在项目仓库创建 Issue

---

感谢您对项目的支持！🎉
