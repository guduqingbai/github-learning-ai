# Self-Thinking AI — 自主思考与自我进化系统

[![GitHub license](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

一个能自我扫描、自我学习、自我修改、并在无人干预下持续进化的 AI 系统。  
v2.0：思考引擎纯本地运行，不依赖任何第三方 AI API。

---

## 核心思想

大多数 AI 系统是"工具"——你输入指令，它输出结果。这个系统不同：

- **它有自己的大脑** — 用知识图、模式引擎、类比引擎进行纯算法思考
- **它自己观察自己** — 用 AST 解析自身代码，知道自己的结构、问题、缺口
- **它对自己好奇** — 基于真实数据生成好奇心问题
- **它自己学习** — 爬虫在后台收集知识，优先学习与自身相关的内容
- **它修改自己** — 发现 bare except 自动修复，发现知识缺口自动补充

思考闭环：

```
扫描（观察自己）
  → 好奇（发现问题）
    → 探索（调查研究）
      → 学习（吸收知识）
        → 行动（修改自己的代码）
          → 再扫描（看变化）
            → 新的好奇心……
```

---

## 快速开始

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
"
```

---

## 架构

```
KnowledgeGraph（知识图：实体 + 关系 + 遍历）
    │
    ├── SelfModel（自模型：AST 分析自身代码）
    ├── PatternEngine（模式引擎：代码缺陷 + 知识模式）
    └── AnalogyEngine（类比引擎：结构相似度 + 跨域连接）
    │
    └── ThinkingEngine（思考引擎：好奇心 + 洞察 + 叙事）
            │
    SelfThinkingAgent（思考编排：学习 → 探索 → 洞察 → 修改）
            │
    ThinkingDaemon（24/7 守护进程，周期性触发思考循环）
```

| 组件 | 文件 | 职责 |
|------|------|------|
| **SelfScanner** | `self_scanner.py` | AST 扫描所有 .py 文件，检测代码质量和系统状态 |
| **CuriosityEngine** | `curiosity_engine.py` | 基于扫描数据生成真实好奇心问题 |
| **KnowledgeGraph** | `knowledge_graph.py` | 实体-关系知识图，纯 dict+list 实现 |
| **SelfModel** | `self_model.py` | 基于 AST 的自身模型，提取能力清单和依赖关系 |
| **PatternEngine** | `pattern_engine.py` | 代码/知识模式发现（bare except、死代码、相似模块） |
| **AnalogyEngine** | `analogy_engine.py` | 结构相似度检测，余弦相似度比较实体指纹 |
| **ThinkingEngine** | `thinking_engine.py` | 大脑核心，整合所有模块生成好奇心+洞察+叙事 |
| **SelfThinkingAgent** | `self_thinking_agent.py` | 思考编排完整流水线 |
| **SelfModificationEngine** | `self_modification_engine.py` | 安全自我修改：备份→验证→git commit→自动回滚 |
| **ThinkingDaemon** | `thinking_daemon.py` | 守护进程，周期性触发思考循环 |
| **CognitiveArchitecture** | `cognitive_architecture.py` | 认知状态驱动：好奇心/创造力/意识动态调节 |

---

## 核心特性

**纯算法思考** — 所有好奇心、洞察、叙事全部由本地算法生成，不依赖任何第三方 AI API（如 OpenAI、Claude 等）。

**可验证的输出** — 每次扫描结果一致（无随机值），每个好奇心问题都可追溯到真实数据。

**安全优先的自我修改** — 多层安全机制：宪法红线 → 范围检查 → 风险评估 → AST 语法验证 → git commit。每次修改自动备份，失败即回滚。

**学习优先级系统** — P0：项目自身知识优先；P1：系统相关概念；P2：其他知识。系统自己判断什么值得学。

---

## 安全说明

本仓库仅包含思考引擎核心。以下能力模块因安全原因不在本仓库中：
- 鼠标键盘操控、浏览器自动化
- 交易监控与执行
- 内容生产流水线

**需要了解的安全事项：**
- `self_modification_engine.py` — 包含自动修改项目代码的能力，有多层安全 Gate 保护
- `thinking_daemon.py` / `watchdog.py` — 创建 24/7 常驻后台进程
- `data/`、`mod_backups/` — 运行时数据和备份目录被 gitignore，不入库

---

## 项目结构

```
├── 核心思考系统
│   ├── self_scanner.py             自我扫描器
│   ├── curiosity_engine.py         好奇心引擎
│   ├── self_thinking_agent.py      思考编排器
│   ├── self_modification_engine.py 自我修改引擎
│   ├── thinking_daemon.py          思考守护进程
│   ├── cognitive_architecture.py   认知架构
│   ├── knowledge_graph.py          知识图
│   ├── self_model.py               自模型
│   ├── pattern_engine.py           模式引擎
│   ├── analogy_engine.py           类比引擎
│   ├── thinking_engine.py          思考引擎
│   ├── thought_buffer.py           思维图存储
│   └── knowledge_base.py / system_state_manager.py
│
├── 实用能力
│   ├── ai_knowledge_crawler.py     知识爬虫
│   └── crawler_daemon.py / bridge
│
├── 后台服务
│   ├── watchdog.py                 看门狗（崩溃自启）
│   └── daemon_launcher.py          统一启动器
│
└── 支持文件
    ├── CLAUDE.md / constitution.py / constitution_gate.py
    ├── requirements.txt
    └── start_daemon.vbs            开机自启入口
```

---

## 验证思考

```bash
# 一致性测试：两次扫描结果一致（无随机值）
python -c "
from self_scanner import SelfScanner;
s = SelfScanner();
a = s.get_full_snapshot();
b = s.get_full_snapshot();
print('✅ 一致' if a['py_files']==b['py_files'] else '❌ 不一致')
"

# 好奇心可追溯：每个问题都来自真实数据
python -c "
from self_scanner import SelfScanner;
from curiosity_engine import CuriosityEngine;
s = SelfScanner();
qs = CuriosityEngine().generate_questions(s.get_full_snapshot());
for q in qs[:3]:
    print(f'[{q.importance}] {q.explore_action}: {q.question[:80]}')
"

# 断开网络也能思考
python -c "
print('✅ 思考引擎纯本地运行，不需要第三方 API')
"
```

---

## 许可证

GNU General Public License v3.0 (GPLv3)
