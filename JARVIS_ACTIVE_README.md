# 🤖 贾维斯主动沟通智能助手

## 🎯 概述

这是一个像钢铁侠中贾维斯那样的智能主动沟通助手，具备以下特性：

- **智能感知**：主动感知您的学习状态和需求
- **自动沟通**：根据学习目标和时间自动发起沟通
- **个性化响应**：根据您的学习风格提供个性化建议
- **任务执行**：自动执行学习任务和项目分析
- **持续监控**：24小时监控学习进度

## 🚀 快速开始

### 1. 测试主动沟通功能

```bash
cd "C:\Users\吴文豪\claude-code-projects\github-learning"
python jarvis_active.py --test
```

### 2. 启动监控系统

```bash
python jarvis_monitor.py
```

## 📋 监控系统命令

启动监控系统后，您可以使用以下命令：

| 命令 | 功能 | 示例 |
|------|------|------|
| `c` | 强制进行主动沟通 | `c` |
| `s` | 停止监控系统 | `s` |
| `q` | 退出程序 | `q` |

## 🔄 主动沟通逻辑

### 自动触发条件

1. **时间间隔**：超过1小时未进行交互
2. **定时通知**：每天9:00、12:00、18:00、21:00
3. **学习状态**：检测学习进度和项目更新

### 沟通内容

- **问候语**：根据时间选择合适的问候
- **对话起始**：智能建议学习或任务
- **学习建议**：基于学习目标的个性化建议
- **任务分析**：当前项目分析和状态报告
- **进度报告**：系统运行状态和专家/知识数量
- **响应处理**：等待您的响应并执行相应操作

## 📊 功能特性

### 1. 智能学习系统

```python
# 学习建议生成
suggestion = assistant._generate_learning_suggestion()
# 输出："我建议您学习Python数据分析项目，这与您的学习目标高度匹配。"

# 任务执行
assistant._execute_learning_plan()
# 输出："分析项目: Python数据分析项目"
```

### 2. 项目分析

```python
projects = assistant.system.process_task({
    "type": "project_analysis",
    "keyword": "Python"
})
# 返回：项目分析结果
```

### 3. 专家系统

```python
experts = assistant.system.process_task({
    "type": "expert_consultation",
    "task_type": "数据分析",
    "skills": ["Python", "Pandas"]
})
# 返回：专家匹配结果
```

### 4. 知识管理

```python
knowledge = assistant.system.process_task({
    "type": "knowledge_management",
    "operation": "retrieve",
    "query": "机器学习"
})
# 返回：知识检索结果
```

## 🛠️ 配置选项

### 用户偏好

配置文件：`data/user_preferences.json`

```json
{
    "name": "用户",
    "learning_goal": "每天学习至少10个项目",
    "preferred_language": "Python",
    "learning_style": "系统学习",
    "notify_times": ["09:00", "12:00", "18:00", "21:00"]
}
```

### 监控设置

修改 `jarvis_monitor.py` 中的配置：

```python
class JarvisMonitor:
    def __init__(self):
        self.assistant = None
        self.running = False
        self.check_interval = 60  # 检查间隔（秒）
```

## 📝 日志和记录

### 对话历史

文件：`data/conversation_history.json`

包含所有的主动沟通历史和用户响应：

```json
[
    {
        "timestamp": "2026-04-28 18:44:30",
        "type": "主动沟通",
        "content": "晚上好！我注意到您的学习进度不错..."
    },
    {
        "timestamp": "2026-04-28 18:44:35",
        "type": "用户响应",
        "content": "是"
    }
]
```

### 系统日志

监控系统实时输出到控制台，记录以下事件：

- ✅ 系统启动/停止
- 📢 主动沟通发生
- ❌ 错误信息
- 📋 任务执行状态

## 🎯 使用场景

### 场景1：学习任务提示

**系统主动**：
```
📢 智能助手主动沟通
============================================================
🤖 晚上好！
🤖 您今天的学习任务已经完成，是否需要学习更多内容？
🤖 我建议您学习Java网络应用，这会增强您的后端开发能力。
🤖 当前有 2 个符合条件的项目需要分析，我建议您立即开始处理。
🤖 当前状态：8个专家系统正常运行，6个知识条目。
🤖 您希望我继续处理什么任务？
```

**用户响应**：
```
🧑 请输入您的响应: 是
🤖 太好了！我立即为您准备学习任务。
📋 执行学习计划...
✅ 分析项目: Python数据分析项目
✅ 分析项目: Java网络应用
🎯 学习计划完成！
```

### 场景2：项目更新提醒

**系统主动**：
```
🤖 根据您的学习目标，我为您准备了今天的学习计划。
🤖 我发现几个您可能感兴趣的新项目，是否需要查看？
🤖 有几个项目更新了，是否需要重新分析？
```

## 🚀 性能优化

### 1. 减少检查频率

修改 `jarvis_monitor.py`：

```python
self.check_interval = 300  # 5分钟检查一次
```

### 2. 调整通知时间

修改 `data/user_preferences.json`：

```json
{
    "notify_times": ["09:00", "18:00"]
}
```

### 3. 限制项目数量

修改 `jarvis_active.py` 中的 `_execute_learning_plan()` 方法：

```python
for project in projects["data"][:2]:  # 只分析前2个项目
    print(f"✅ 分析项目: {project['name']}")
```

## 🔧 故障排除

### 问题1：初始化失败

**症状**：
```
❌ 初始化助手失败
```

**解决方法**：
- 检查 `data/experts.json` 和 `data/knowledge_base.json` 文件是否存在
- 确保文件内容格式正确（JSON格式）
- 重新运行 `jarvis_active.py --test` 初始化数据

### 问题2：项目分析失败

**症状**：
```
❌ 执行学习计划失败
```

**解决方法**：
- 检查网络连接是否正常
- 验证GitHub API访问是否受限
- 重新运行 `python jarvis_active.py --test`

### 问题3：内存泄漏

**症状**：
- 系统长时间运行后占用大量内存

**解决方法**：
- 定期重启监控系统
- 优化数据加载策略
- 减少检查频率

## 📈 改进计划

### 版本2.0

- [ ] 支持多用户管理
- [ ] 机器学习模型优化
- [ ] 更自然的语言生成
- [ ] 集成日历和提醒功能
- [ ] 移动端支持

### 版本3.0

- [ ] 情感分析和个性化响应
- [ ] 图像识别和视频处理
- [ ] 语音识别和合成
- [ ] AR/VR接口
- [ ] 物联网设备集成

## 📞 技术支持

如果您遇到任何问题，或有功能建议：

1. **查看日志**：检查控制台输出的错误信息
2. **重新初始化**：运行 `jarvis_active.py --test`
3. **重置数据**：删除 `data/` 目录下的JSON文件，重新运行
4. **联系开发**：请保留完整的错误日志

---

**🎯 祝您学习愉快！** 🚀
