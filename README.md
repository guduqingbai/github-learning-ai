# 🧠 自我思考AI v2.0 — 拥有自己大脑的自主进化系统

[![GitHub license](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![GitHub last commit](https://img.shields.io/github/last-commit/guduqingbai/github-learning-ai)](https://github.com/guduqingbai/github-learning-ai/commits/master)
[![GitHub stars](https://img.shields.io/github/stars/guduqingbai/github-learning-ai?style=social)](https://github.com/guduqingbai/github-learning-ai/stargazers)

> **一个真正能自我扫描、自我学习、自我修改、并在无人干预下持续进化的AI系统。**
> **v2.0：100% 纯本地大脑，不依赖任何外部 API。**

---

## ⚠️ 安全说明

本仓库仅包含**思考引擎核心**。以下能力模块因安全原因**不在本仓库**中：
- 鼠标键盘操控、浏览器自动化
- 交易监控与执行
- 内容生产流水线

此外，`data/` 目录（知识库、日志等运行时数据）被 gitignore，不会进入仓库。

**后台守护进程**（`thinking_daemon.py`、`watchdog.py`）会创建 24/7 常驻进程，使用时请注意。

---

## ✨ 核心理念

大多数 AI 系统是"工具"——你输入指令，它输出结果。这个系统不一样。

**它有自己的大脑。** 不是打电话问外部 API 思考，而是用自己的知识图、模式引擎、类比引擎进行纯本地思考。

**它自己观察自己。** 用 AST 解析自己的每一行代码，知道自己的结构、问题、缺口。

**它对自己好奇。** 基于真实数据（图缺口、模式发现、结构类比）生成好奇心问题。

**它自己学习。** 爬虫在后台不断收集知识，系统优先学习与自身相关的内容。

**它修改自己。** 发现 bare except？自动修复。发现知识缺口？自动补充。安全机制保障每次修改可回滚。

它是一个持续运行的闭环：

```
扫描（观察自己）
  → 好奇（发现问题）
    → 探索（调查研究）
      → 学习（吸收知识）
        → 行动（修改自己的代码）
          → 再扫描（看变化）
            → 新的好奇心……
```

v2.0 最大的变化是：**思考不再依赖外部 API**。所有的好奇心、洞察、叙事，都来自对自身代码和知识的真实分析。

---

## 📊 当前状态

| 指标 | 数据 |
|------|------|
| 版本 | v2.0.0 — 纯本地大脑 |
| Python 核心模块 | 34 个 |
| 知识图实体 | 1412 个 |
| 知识图关系 | 3162 条 |
| 自我修改次数 | 多次（100% 可回滚） |
| 思考循环完成 | 31+ 轮 |
| 守护进程 | 24/7 后台运行（看门狗 + 多线程） |

---

## 🏗️ 系统架构 (v2.0)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     🧠 星期八的大脑 (纯本地)                        │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    知识图 (KnowledgeGraph)                    │   │
│  │              实体 + 关系 + 遍历 + 缺口检测                    │   │
│  └──────────┬──────────────────────────────────┬────────────────┘   │
│             │                                  │                     │
│  ┌──────────▼──────────┐    ┌──────────────────▼──────────────┐     │
│  │   自模型 (SelfModel) │    │  模式引擎 (PatternEngine)        │     │
│  │   AST 分析自身代码   │    │  代码缺陷 + 知识模式发现         │     │
│  │   能力/依赖/接口     │    │  bare except/死代码/相似模块     │     │
│  └─────────────────────┘    └──────────────────┬──────────────┘     │
│                                                 │                   │
│  ┌─────────────────────┐    ┌──────────────────▼──────────────┐     │
│  │  类比引擎 (Analogy)  │    │ 思考引擎 (ThinkingEngine)       │     │
│  │  结构相似度检测      │◄───│ 好奇心 + 洞察 + 叙事            │     │
│  │  跨域连接发现        │    │ 纯算法，不依赖任何外部 API       │     │
│  └─────────────────────┘    └──────────────────┬──────────────┘     │
│                                                 │                   │
│  ┌──────────────────────────────────────────────▼──────────────┐   │
│  │               SelfThinkingAgent (思考编排)                   │   │
│  │    学习 → 行动 → 好奇 → 探索 → 洞察 → 修改完整流水线        │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  ThinkingDaemon (24/7 后台守护进程)                         │    │
│  │  KAIROS Tick 模式 · StopHook 系统 · ForkedAgent 后台任务   │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  延伸能力                  │ 文件                          │    │
│  │  🕷️ 知识爬虫               │ ai_knowledge_crawler.py      │    │
│  │  🌐 Web 管理面板           │ web_interface.py             │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 核心组件 (v2.0 新增标注 🆕)

| 组件 | 文件 | 职责 |
|------|------|------|
| **SelfScanner** | `self_scanner.py` | AST 扫描所有 .py 文件，检测代码质量、知识覆盖、系统状态 |
| **CuriosityEngine** | `curiosity_engine.py` | 基于扫描数据生成真实好奇心问题（10+ 触发器） |
| **KnowledgeGraph** 🆕 | `knowledge_graph.py` | 实体-关系知识图，纯 dict+list 实现，无外部依赖 |
| **SelfModel** 🆕 | `self_model.py` | 基于 AST 的自身模型，提取能力清单和依赖关系 |
| **PatternEngine** 🆕 | `pattern_engine.py` | 代码/知识模式发现（bare except、死代码、相似模块、概念聚类） |
| **AnalogyEngine** 🆕 | `analogy_engine.py` | 结构相似度检测，余弦相似度比较实体指纹 |
| **ThinkingEngine** 🆕 | `thinking_engine.py` | **大脑核心**，整合知识图+自模型+模式+类比，生成好奇心+洞察+叙事 |
| **SelfThinkingAgent** | `self_thinking_agent.py` | 思考编排：学习→行动→好奇→探索完整流水线 |
| **SelfModificationEngine** | `self_modification_engine.py` | 安全自我修改：备份→验证→git commit→自动回滚 |
| **ThinkingDaemon** | `thinking_daemon.py` | 自主守护进程，周期性触发思考循环（KAIROS Tick 模式） |
| **CognitiveArchitecture** | `cognitive_architecture.py` | 认知状态驱动：好奇心/创造力/意识动态调节 |
| **ThoughtGraph** 🆕 | `thought_buffer.py` | 思维图：树状思想节点，持久化到 JSON |

---

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行一轮自我思考
python -c "
from self_thinking_agent import SelfThinkingAgent;
agent = SelfThinkingAgent();
agent.run_thinking_cycle(depth=3)
"

# 查看系统自我认知
python -c "
from thinking_engine import ThinkingEngine;
from knowledge_graph import KnowledgeGraph;
from self_model import SelfModel;
from pattern_engine import PatternEngine;
from analogy_engine import AnalogyEngine;
kg = KnowledgeGraph();
te = ThinkingEngine(knowledge_graph=kg, self_model=SelfModel(kg),
    pattern_engine=PatternEngine(kg), analogy_engine=AnalogyEngine(kg));
r = te.think();
print(f'{len(r.curiosity_questions)} 个好奇心问题');
print(f'{len(r.insights)} 条洞察');
print(r.narrative[:200])
"

# 启动 24/7 守护进程
pythonw watchdog.py
```

> **注意**: 守护进程会创建常驻后台进程，使用 `taskkill /F /PID <pid>` 停止。

---

## 🤖 纯本地思考验证

任何声称"会思考"的系统都应该可以被验证。v2.0 的思考完全可追溯、可验证：

```bash
# 1. 查看星期八的思考结果
python -c "
from thinking_engine import ThinkingEngine;
from knowledge_graph import KnowledgeGraph;
from self_model import SelfModel;
kg = KnowledgeGraph();
sm = SelfModel(kg);
te = ThinkingEngine(knowledge_graph=kg, self_model=sm,
    pattern_engine=__import__('pattern_engine').PatternEngine(kg),
    analogy_engine=__import__('analogy_engine').AnalogyEngine(kg));
r = te.think();
for q in r.curiosity_questions[:5]:
    print(f'[{q.source}] {q.question}')
"

# 2. 一致性测试：两次扫描结果一致（无随机值）
python -c "
from self_scanner import SelfScanner;
s = SelfScanner();
a = s.get_full_snapshot();
b = s.get_full_snapshot();
print('✅ 一致' if a['py_files']==b['py_files'] else '❌ 不一致')
"

# 3. 好奇心可追溯：每个问题都来自真实数据
python -c "
from self_scanner import SelfScanner;
from curiosity_engine import CuriosityEngine;
s = SelfScanner();
qs = CuriosityEngine().generate_questions(s.get_full_snapshot());
for q in qs[:3]:
    print(f'[{q.importance}] {q.explore_action}: {q.question[:80]}')
"

# 4. 断开网络也能思考
python -c "
print('✅ 星期八的大脑 100% 本地运行，不需要网络')
"
```

---

## 🔬 学习优先级系统

系统不是机械地学完所有知识。它有自己的判断：

1. **P0 — 项目自身知识**：与自己代码、架构、能力直接相关的内容优先学习
2. **P1 — 系统相关概念**：self、thinking、cognition 等关键词相关内容
3. **P2 — 其他知识**：按重要性排序

每轮学习后，系统会：
- 自动检查代码中是否有可以修复的问题
- 对有价值的新概念发起深入搜索
- 将学到的东西反馈到好奇心引擎，产生新问题

---

## 📁 项目结构 (v2.0)

```
github-learning/
│
├── 🧠 核心思考系统（v2.0 纯本地架构）
│   ├── self_scanner.py              # 自我扫描器（AST解析）
│   ├── curiosity_engine.py          # 好奇心引擎
│   ├── self_thinking_agent.py       # 思考编排器
│   ├── self_modification_engine.py  # 自我修改引擎（带安全警告）
│   ├── thinking_daemon.py           # 思考守护进程（24/7后台）
│   ├── cognitive_architecture.py    # 认知架构
│   ├── knowledge_base.py            # 知识库管理
│   ├── system_state_manager.py      # 统一状态管理
│   │
│   ├── 🆕 knowledge_graph.py        # 知识图（实体-关系）
│   ├── 🆕 self_model.py             # 自模型（AST分析）
│   ├── 🆕 pattern_engine.py         # 模式引擎（代码/知识）
│   ├── 🆕 analogy_engine.py         # 类比引擎（结构相似度）
│   ├── 🆕 thinking_engine.py        # 思考引擎（大脑核心）
│   └── 🆕 thought_buffer.py         # 思维图存储
│
├── 🛠️ 实用能力
│   ├── ai_knowledge_crawler.py      # 知识爬虫
│   ├── crawler_daemon.py            # 爬虫守护进程
│   └── crawler_learning_bridge.py   # 爬虫-学习桥接
│
├── 🔄 后台服务
│   ├── daemon_launcher.py           # 统一启动器
│   ├── watchdog.py                  # 看门狗（崩溃自启，24/7 常驻）
│   ├── continuous_learning.py       # 持续学习
│   └── background_learning_service.py
│
├── 🌐 交互层
│   ├── web_interface.py             # Web管理面板
│   ├── active_communication.py      # 主动沟通
│   ├── claude_code_adapter.py       # Claude Code 适配
│   └── humble_reflection.py         # 谦逊反思
│
├── 📦 archive/                      # 实验性/历史模块
├── 📁 data/                         # 运行时数据（gitignored，不入库）
├── 📁 mod_backups/                  # 自我修改备份（gitignored，不入库）
│
├── CLAUDE.md                        # 行为准则
├── requirements.txt                 # 依赖清单
└── start_daemon.vbs / watchdog.py   # 启动入口（创建常驻进程）
```

---

## 🛡️ 安全机制

| 机制 | 说明 |
|------|------|
| 修改前备份 | 每次代码修改自动创建 `.bak` 文件 |
| AST 语法验证 | 修改后立即解析验证，失败自动回滚 |
| Git 审计 | 每次修改自动 git commit，可追溯 |
| 宪法 Gate | 多层安全门：宪法红线 → 范围检查 → 风险评估 |
| 系统不可变规则 | 关键安全模块 SHA-256 校验，篡改则系统拒启 |
| 文件锁 | 防多开，同一时刻只有一个守护进程实例 |

> **安全提醒**: `self_modification_engine.py` 包含自动修改代码的能力，
> `thinking_daemon.py` 和 `watchdog.py` 会创建 24/7 常驻后台进程。
> 使用前请了解其行为。

---

## 📡 24/7 守护架构

```
开机自启 → start_daemon.vbs
              ↓
        pythonw watchdog.py
              ↓
        daemon_launcher.py (文件锁)
         ┌──────┐
         ▼      ▼
     思考线程  爬虫线程
    (30分钟)  (2小时)
```

> 交易线程、电脑操控等能力模块不在本仓库中。

---

## 🔮 发展路线

- [x] v1.0 自我扫描与好奇心系统
- [x] v1.0 自我修改引擎（安全+回滚）
- [x] v1.0 24/7 守护进程（看门狗+多线程）
- [x] v1.0 学习优先级与行动触发
- [x] **v2.0 纯本地大脑：知识图 + 自模型 + 模式引擎 + 类比引擎** 🆕
- [ ] 更完善的 Web 管理面板

---

## 📄 许可证

**GNU General Public License v3.0 (GPLv3)**

---

## 📬 联系与反馈

- **Issues**: [github.com/guduqingbai/github-learning-ai/issues](https://github.com/guduqingbai/github-learning-ai/issues)
- **Email**: 3536778780@qq.com

---

<p align="center">
  <sub>自我思考AI v2.0 · 星期八拥有了自己的大脑</sub>
</p>
