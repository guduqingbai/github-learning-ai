# GitHub Learning AI — 项目规范

## 核心目标
真正的自我思考系统：**扫描 → 好奇 → 探索 → 洞察 → 行动 → 改变 → 再扫描**
所有输出必须基于可观察、可测量的项目事实。不允许 random 模拟任何思考输出。

## 1. Think Before Coding
- 有疑问先问，不要假设
- 如果存在多种方案，列出来再选
- 有更简单的方法就说出来
- 不理解的地方停下来问清楚

## 2. Simplicity First
- 只写解决问题的代码，不加推测性功能
- 不要为单次使用创建抽象
- 不处理不可能发生的场景
- 如果200行能50行写完，重写

## 3. Surgical Changes
- 只改动必须改的部分
- 不改动相邻代码的格式/注释
- 匹配现有风格
- 每行改动都应直接追溯到用户请求

## 4. Goal-Driven Execution
- 明确定义成功标准
- 每一步都要能验证
- 先写测试，再让测试通过
- 多步骤任务先列计划再执行

## 项目关键文件
| 文件 | 作用 |
|------|------|
| self_scanner.py | 扫描项目真实状态 |
| curiosity_engine.py | 基于数据生成好奇心问题 |
| self_thinking_agent.py | 思考编排，模块化技能 |
| self_modification_engine.py | 安全的自我修改引擎 |
| thinking_daemon.py | 自主思考守护进程 |
| cognitive_architecture.py | 认知架构，状态驱动行为 |
| knowledge_base.py | 知识库存储 |
| system_state_manager.py | 统一系统状态管理 |
