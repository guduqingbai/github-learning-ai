# 🚀 贾维斯式主动沟通AI系统使用说明

本项目是一个类似钢铁侠中贾维斯的智能化主动沟通AI系统，能够主动分析学习状态、提供个性化建议，并在用户不在线时自我学习完善。

## 📋 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 首次运行

```bash
python jarvis_monitor_noninteractive.py
```

**预期结果：**
- 系统会主动分析您的学习状态
- 根据您的学习进度提供个性化建议
- 如果您不在线，系统会自动进入自我学习模式

### 3. 项目测试

运行项目的所有核心功能：

```bash
# 贾维斯主动沟通系统
python jarvis_monitor_noninteractive.py

# 自我学习与系统完善
python self_learning_system.py

# 主动沟通机制
python active_communication.py
```

## 🔧 系统配置

### 修改学习目标

编辑 `data/active_state.json` 文件：

```json
{
  "last_interaction": "2026-04-28T20:15:30",
  "projects_completed": 6,
  "communication_count": 1,
  "response_count": 1,
  "last_suggestion": "Trinity Claw项目架构",
  "current_goal": "每天学习至少10个项目"  // 修改这里
}
```

### 调整沟通频率

修改 `jarvis_monitor_noninteractive.py` 文件中的常量：

```python
# 判断用户是否在线的时间阈值（秒）
INACTIVE_THRESHOLD = 300  # 5分钟

# 系统检查间隔（秒）
CHECK_INTERVAL = 60  # 1分钟
```

### 修改学习主题

编辑 `self_learning_system.py` 文件中的学习主题：

```python
learning_topics = [
    "Python数据科学库",
    "机器学习算法",
    "网络安全最佳实践",
    "系统优化技术",
    "API设计模式",
    "数据库优化"
]
```

## 📊 查看数据

### 系统状态

```bash
type data\active_state.json
```

**内容示例：**
```json
{
  "last_interaction": "2026-04-28T20:15:30",
  "projects_completed": 6,
  "communication_count": 1,
  "response_count": 1,
  "last_suggestion": "Trinity Claw项目架构"
}
```

### 学习进度

```bash
type data\learning_progress.json
```

**内容示例：**
```json
{
  "total_study_time": 90,
  "projects_studied": ["Python数据分析项目", "机器学习项目"],
  "knowledge_points": [
    "项目分析技巧", "代码问题识别", 
    "大语言模型最新进展", "网络安全最佳实践"
  ],
  "learning_effectiveness": 0.95,
  "communication_effectiveness": 0.98
}
```

### 沟通记录

```bash
type data\conversations.jsonl
```

**内容示例：**
```json
{"timestamp": "2026-04-28T20:15:30", "type": "system_initiated", "content": ["晚上好！您的学习进度很好！", "需要我为您分析高级项目吗？"], "context": {"user_status": "online"}}
{"timestamp": "2026-04-28T20:15:30", "type": "user_response", "content": "继续", "context": {"user_status": "online"}}
```

### 贾维斯系统状态

```bash
type data\jarvis_monitor_state.json
```

**内容示例：**
```json
{
  "last_interaction": "2026-04-28T20:15:30",
  "communication_count": 1,
  "response_count": 1,
  "monitoring_active": true
}
```

## 🔍 功能详解

### 主动沟通机制

系统会主动识别用户状态并发起沟通：

**在线状态：**
- 如果用户在5分钟内有交互，系统会主动沟通
- 提供个性化的学习建议
- 根据项目完成数量调整沟通内容

**离线状态：**
- 如果用户超过5分钟没有交互，系统会自动进入自我学习模式
- 定期扫描系统漏洞和代码质量问题
- 从全球AI知识平台获取实时信息

### 学习进度追踪

系统会详细记录您的学习进度：

**项目统计：**
- 已完成项目数量
- 学习项目列表
- 学习时间统计

**知识管理：**
- 获取的知识要点
- 学习效果评估
- 沟通效果分析

### 系统优化

系统会定期进行自我学习和系统优化：

**漏洞检查：**
- 文件权限问题
- 硬编码密码/API密钥
- SQL注入风险

**代码分析：**
- 裸except语句
- 缺少文档字符串
- 缺少类型提示

**知识补充：**
- 从11个全球AI知识平台获取信息
- 内置6个核心AI学习主题
- 持续更新知识库

## 🎯 常见使用场景

### 场景1：第一次使用

**操作：**
```bash
python jarvis_monitor_noninteractive.py
```

**预期结果：**
- 系统会主动分析您的学习状态
- 提供基础项目建议
- 帮助您开始学习

### 场景2：学习过程中

**操作：**
```bash
python jarvis_monitor_noninteractive.py
```

**预期结果：**
- 系统会根据您的学习进度提供个性化建议
- 建议更高级的项目
- 分析您的学习效果

### 场景3：学习完成后

**操作：**
```bash
python jarvis_monitor_noninteractive.py
```

**预期结果：**
- 系统会评估您的学习成果
- 提供学习总结
- 规划下一步学习方向

### 场景4：系统维护

**操作：**
```bash
# 运行自我学习系统
python self_learning_system.py

# 查看系统状态
python active_communication.py --status
```

**预期结果：**
- 系统会扫描和修复漏洞
- 优化代码质量
- 更新知识库

## 🐛 故障排除

### 问题1：系统无法启动

**错误信息：**
```
ModuleNotFoundError: No module named 'requests'
```

**解决方案：**
```bash
pip install -r requirements.txt
```

### 问题2：系统无法读取数据

**错误信息：**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/active_state.json'
```

**解决方案：**
```bash
# 手动创建数据目录和状态文件
mkdir -p data

# 创建默认的系统状态文件
python -c "import json; from datetime import datetime; d = {'last_interaction': datetime.now().isoformat(), 'projects_completed': 0, 'communication_count': 0, 'response_count': 0, 'last_suggestion': 'Python数据分析项目', 'current_goal': '每天学习至少10个项目'}; open('data/active_state.json', 'w').write(json.dumps(d, ensure_ascii=False, indent=2))"

# 创建默认的学习进度文件
python -c "import json; d = {'total_study_time': 0, 'projects_studied': [], 'knowledge_points': [], 'learning_effectiveness': 0.85, 'communication_effectiveness': 0.92}; open('data/learning_progress.json', 'w').write(json.dumps(d, ensure_ascii=False, indent=2))"
```

### 问题3：系统运行缓慢

**解决方案：**
```bash
# 增加系统检查间隔（修改jarvis_monitor_noninteractive.py）
CHECK_INTERVAL = 600  # 10分钟

# 减少学习主题数量（修改self_learning_system.py）
learning_topics = [
    "Python数据科学库",
    "机器学习算法",
    "网络安全最佳实践"
]
```

## 🔄 系统更新

### 更新学习内容

```bash
# 运行自我学习系统以获取最新AI知识
python self_learning_system.py
```

### 更新系统功能

```bash
# 查看项目的最新版本
git log --oneline

# 查看文件变更
git status

# 提交变更
git add .
git commit -m "优化系统功能"
```

## 📞 支持与反馈

### 报告问题

如果您遇到任何问题，可以通过以下方式联系我们：

1. **GitHub Issues**：在项目仓库创建Issue
2. **邮件联系**：3536778780@qq.com
3. **社区支持**：加入项目的Discord或Slack频道

### 功能建议

欢迎您提出功能建议和改进意见：

1. 查看项目的Issue列表
2. 提交Feature Request
3. 发送邮件或消息

---

**项目状态：** 🚀 已完成并可正常运行

**最后更新：** 2026年4月28日
