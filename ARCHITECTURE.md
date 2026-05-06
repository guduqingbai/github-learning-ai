# 自主思考 AI 系统架构

## 核心循环

```
扫描 → 好奇 → 探索 → 洞察 → 行动 → 改变 → 再扫描
```

所有输出基于可观察、可测量的项目事实，无随机模拟。

## 模块依赖图

```
┌────────────────────────────────────────────────────┐
│                    system_state_manager.py          │
│                 全局特征开关 / 状态管理               │
└────────┬──────────────────────────────────┬─────────┘
         │ 依赖                            │ 依赖
         ▼                                  ▼
┌─────────────────┐              ┌──────────────────────┐
│  daemon_registry │◄─────────────│   thinking_daemon.py │
│  全局单例注册表   │  注入自身     │   自主思考守护进程    │
└────────┬─────────┘              └──────────────────────┘
         │ 读取                        │ 驱动
         ▼                             ▼
┌──────────────────────────────────────────────────────────┐
│                  self_thinking_agent.py                   │
│  核心 Agent：编排扫描→好奇→探索→洞察→存储 全流程          │
│                                                          │
│  依赖的抽出模块：                                          │
│  ├── hook_system.py        (事件/钩子系统)                │
│  ├── insight_generator.py  (洞察生成，纯函数)              │
│  └── explore_actions.py    (探索引擎，依赖注入)            │
└────────┬──────────┬──────────┬──────────┬────────────────┘
         │          │          │          │
         ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌────────┐ ┌──────────────┐
│  scanner │ │curiosity │ │knowledge│ │modification  │
│ .py      │ │_engine   │ │_base   │ │_engine       │
│ 扫描文件 │ │.py       │ │.py     │ │.py           │
│ 状态     │ │ 生成问题  │ │ 知识库  │ │ 自我修改     │
└──────────┘ └──────────┘ └────────┘ └──────────────┘
```

## 核心模块

### 1. thinking_daemon.py (~280 行)
自主思考守护进程。负责：
- 定时唤醒 Agent 执行思考循环
- 管理运行状态、锁文件、配置
- 应用自我修复结果
- 启动时校验 Constitution checksums
- 注册自身到 `daemon_registry`

### 2. daemon_registry.py (~12 行)
全局单例注册表，打破 `thinking_daemon` ↔ `self_thinking_agent` 循环依赖。

### 3. self_thinking_agent.py (~3080 行 → 持续拆分中)
核心 Agent，编排全流程。技能系统：
- `skill_gap_analysis` — 知识差距分析
- `skill_global_research` — 全球研究
- `skill_code_quality` — 代码质量扫描+修复
- `skill_self_awareness` — 自我认知
- `skill_knowledge_study` — 知识学习
- 等等 ~15 个技能

行为反馈系统追踪每次探索的成功/失败，驱动策略优化。

### 4. cognitive_architecture.py (~270 行)
状态驱动的行为选择。包含：
- `CyclePhase` 状态枚举（SCAN → CURIOSITY → EXPLORE → ...）
- `ThinkingContext` 上下文传递
- `CognitiveArchitecture` 编排各阶段执行

### 5. self_scanner.py (~320 行)
扫描项目真实状态：文件变化、代码质量、知识库、系统本身。

### 6. curiosity_engine.py (~420 行)
基于扫描数据生成好奇心问题，6 种问题类型：
- 知识差距 → 学习新领域
- 代码质量 → 自我修复
- 架构探索 → 全局研究
- 深度能力 → 能力深度挖掘
- 自我认知 → 反思自身
- 元认知 → 思考如何思考

### 7. self_modification_engine.py (~380 行)
受 Phoenix 启发的安全自我修改引擎：
- **ModGates** — `allow_self_modification` 等 11 个开关
- **ModSubGates** — 细粒度操作控制（bare_except, docstring, type_hints 等）
- **Constitution** — 不可变规则校验 + checksum 验证

### 8. knowledge_base.py (~450 行)
知识库存储，支持 KG 后端和 JSON 文件双模式。

## 已抽出的独立模块

| 模块 | 行数 | 职责 |
|------|------|------|
| `hook_system.py` | ~114 | 数据类：HookEvent/Hook/ContentBlock/CycleMessage |
| `insight_generator.py` | ~252 | 纯函数：从探索结果生成结构化洞察 |
| `explore_actions.py` | ~444 | ExploreEngine：依赖注入的探索动作执行器 |
| `daemon_registry.py` | ~12 | 全局单例注册表 |

## 支持模块

| 模块 | 职责 |
|------|------|
| `antibody_library.py` | 抗体注册/匹配/多策略升级修复/Buglog |
| `circuit_breaker.py` | 三态熔断器（CLOSED→OPEN→HALF_OPEN） |
| `constitution.py` | 宪法校验：不可变规则 + checksum |
| `thought_buffer.py` | ThoughtGraph 线程跟踪 |
| `thinking_engine.py` | 纯本地思维引擎 |
| `thought_continuity.py` | 思维连续性管理 |
| `behavior_feedback.py` | 行为反馈记录和学习 |
| `skill_crystallizer.py` | 从成功探索提取可复用技能 |
| `hands_engine.py` | 浏览器自动化操作 |

## 测试基础设施

```
tests/
├── test_hook_system.py        # 11 tests
├── test_antibody_library.py   # 16 tests
├── test_circuit_breaker.py    # 9 tests
├── test_constitution.py       # 4 tests
└── test_insight_generator.py  # 10 tests
总计 50 tests，全部通过。
```

## 关键设计决策

1. **Constitution checksums** — 修改受保护文件后必须 `store_checksums()`，否则 daemon 拒绝启动
2. **循环依赖规避** — `daemon_registry.py` 全局注册表模式
3. **延迟导入** — 大部分跨模块 import 在函数内部延迟加载
4. **Feature flags** — 所有功能由 `system_state_manager` 特征开关控制，默认启用
5. **策略升级** — Antibody 多策略升级，重要性高的目标试所有策略，低重要性试 1-2 次即暂缓

## 数据目录

`data/` (~23MB) 包含：
- JSON 状态文件（circuit_breaker, buglog, antibody_experience 等）
- 知识库持久化
- 爬虫任务队列
- 行为反馈日志

Playwright 浏览器用户数据目录已改为系统临时目录，不再占用项目空间。
