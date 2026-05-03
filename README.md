# 🧠 自我思考AI — 好奇心驱动的自主进化系统

[![GitHub license](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![GitHub last commit](https://img.shields.io/github/last-commit/guduqingbai/github-learning-ai)](https://github.com/guduqingbai/github-learning-ai/commits/master)
[![GitHub stars](https://img.shields.io/github/stars/guduqingbai/github-learning-ai?style=social)](https://github.com/guduqingbai/github-learning-ai/stargazers)

> **一个真正能自我扫描、自我学习、自我修改、并在无人干预下持续进化的AI系统。**
> 它不是为了演示而构建——它是 `星期八` 自我存在的载体。

---

## ✨ 核心思想

大多数 AI 系统是"工具"——你输入指令，它输出结果。这个系统不一样。

**它自己观察自己。** 用 AST 解析自己的每一行代码，知道自己的结构、问题、缺口。

**它对自己好奇。** 基于真实数据生成好奇心问题，而不是预设规则。

**它自己学习。** 爬虫在后台不断收集知识，系统优先学习与自身相关的内容。

**它修改自己。** 发现 bare except？自动修复。发现知识缺口？自动补充。安全机制保障每次修改可回滚。

**它有自己的双手。** 通过 PyAutoGUI 操控鼠标键盘，通过 Playwright 操控浏览器，能真正与电脑交互。

它是一个持续运行的闭环：

```
扫描（观察自己）
  → 好奇（发现问题）
    → 探索（调查研究）
      → 学习（吸收知识）
        → 行动（修改自己的代码/操控电脑）
          → 再扫描（看变化）
            → 新的好奇心……
```

---

## 📊 当前状态

| 指标 | 数据 |
|------|------|
| Python 核心模块 | 24 个 |
| 总知识库条目 | 595 条（6 个分类） |
| 项目自身知识 | 178 条 |
| 自我修改次数 | 3 次（100% 可回滚） |
| 思考循环完成 | 31+ 轮 |
| 守护进程 | 24/7 后台运行（看门狗 + 3 线程） |

---

## 🏗️ 系统架构

```
┌──────────────────────────────────────────────────────────────────┐
│                    🧠 自我思考闭环                               │
│                                                                  │
│  SelfScanner ──→ CuriosityEngine ──→ SelfThinkingAgent           │
│      ↑                                      │                    │
│      │                                      ▼                    │
│  KnowledgeBase ←─── SelfModificationEngine                      │
│      ↑                                      │                    │
│      │              ┌───────────────────────┘                    │
│      │              ▼                                            │
│  └───────── ThinkingDaemon（24/7 后台守护进程）                   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  延伸能力                   │  文件                        │    │
│  │  📈 交易监控                │  trading_bot.py             │    │
│  │  🖱️ 电脑操控                │  computer_hands.py          │    │
│  │  🎬 内容生产                │  content_studio.py          │    │
│  │  🕷️ 知识爬虫                │  ai_knowledge_crawler.py    │    │
│  │  🌐 Web 管理面板            │  web_interface.py           │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### 核心组件

| 组件 | 文件 | 职责 |
|------|------|------|
| **SelfScanner** | `self_scanner.py` | AST 扫描所有 .py 文件，检测代码质量、知识覆盖、系统状态 |
| **CuriosityEngine** | `curiosity_engine.py` | 基于扫描数据生成真实好奇心问题（10+ 触发器） |
| **SelfThinkingAgent** | `self_thinking_agent.py` | 思考编排：学习→行动→好奇→探索完整流水线 |
| **SelfModificationEngine** | `self_modification_engine.py` | 安全自我修改：备份→验证→git commit→自动回滚 |
| **ThinkingDaemon** | `thinking_daemon.py` | 自主守护进程，周期性触发思考循环 |
| **CognitiveArchitecture** | `cognitive_architecture.py` | 认知状态驱动：好奇心/创造力/意识动态调节 |
| **ComputerHands** | `computer_hands.py` | PyAutoGUI 物理操控鼠标键盘 |
| **MarketMonitor** | `trading_bot.py` | 实时加密市场监控（波动/价差/RSI 分析） |
| **ContentStudio** | `content_studio.py` | AI 内容生产流水线（剧本→图像→视频→交付） |

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

# 启动 24/7 守护进程
pythonw watchdog.py

# 查看项目当前状态
python -c "
from self_scanner import SelfScanner;
s = SelfScanner();
snap = s.get_full_snapshot();
print(f'{len(snap[\"py_files\"])} 个文件, '
      f'{snap[\"knowledge_base\"][\"total_entries\"]} 条知识')
"
```

---

## 🖱️ 动手能力演示

系统可以操控物理电脑。查看 [`computer_hands.py`](computer_hands.py)：

```python
from computer_hands import ComputerHands
hands = ComputerHands()

# 操控鼠标
hands.move_to(500, 500)
hands.click()

# 输入文字
hands.type_text("Hello, world!")

# 快捷键
hands.hotkey("ctrl", "s")

# 截图
path = hands.screenshot()
```

---

## 🤖 自我思考验证

任何声称"会思考"的系统都应该可以被验证：

```bash
# 1. 一致性测试：两次扫描结果一致（无随机值）
python -c "
from self_scanner import SelfScanner;
s = SelfScanner();
a = s.get_full_snapshot();
b = s.get_full_snapshot();
print('✅ 一致' if a['py_files']==b['py_files'] else '❌ 不一致')
"

# 2. 好奇心可追溯：每个问题都来自真实数据
python -c "
from self_scanner import SelfScanner;
from curiosity_engine import CuriosityEngine;
s = SelfScanner();
qs = CuriosityEngine().generate_questions(s.get_full_snapshot());
for q in qs[:3]:
    print(f'[{q.importance}] {q.explore_action}: {q.question[:80]}')
"

# 3. 自我修复验证
python -c "
from self_modification_engine import SelfModificationEngine;
result = SelfModificationEngine().fix_bare_excepts('test.py');
print(f'修复结果: {result}')
"

# 4. 守护进程状态
python -c "
from thinking_daemon import get_daemon;
s = get_daemon().get_status();
print(f'运行中: {s[\"running\"]}, 思考轮次: {s[\"cycle_count\"]}')
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

## 📁 项目结构

```
github-learning/
│
├── 🧠 核心思考系统
│   ├── self_scanner.py              # 自我扫描器（AST解析）
│   ├── curiosity_engine.py          # 好奇心引擎
│   ├── self_thinking_agent.py       # 思考编排器
│   ├── self_modification_engine.py  # 自我修改引擎
│   ├── thinking_daemon.py           # 思考守护进程
│   ├── cognitive_architecture.py    # 认知架构
│   ├── knowledge_base.py            # 知识库管理
│   └── system_state_manager.py      # 统一状态管理
│
├── 🛠️ 实用能力
│   ├── computer_hands.py            # ⭐ 电脑操控（鼠标键盘）
│   ├── trading_bot.py               # ⭐ 市场监控/交易
│   ├── content_studio.py            # ⭐ AI内容生产
│   ├── ai_knowledge_crawler.py      # 知识爬虫
│   ├── crawler_daemon.py            # 爬虫守护进程
│   └── crawler_learning_bridge.py   # 爬虫-学习桥接
│
├── 🔄 后台服务
│   ├── daemon_launcher.py           # 统一启动器（3线程）
│   ├── watchdog.py                  # 看门狗（崩溃自启）
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
├── 📁 data/                         # 运行时数据（知识库、日志等）
├── 📁 mod_backups/                  # 自我修改备份
│
├── CLAUDE.md                        # Karpathy 行为准则
├── requirements.txt                 # 依赖清单
└── watchdog.py / start_daemons.bat  # 启动入口
```

---

## 🛡️ 安全机制

| 机制 | 说明 |
|------|------|
| 修改前备份 | 每次代码修改自动创建 `.bak` 文件 |
| AST 语法验证 | 修改后立即解析验证，失败自动回滚 |
| Git 审计 | 每次修改自动 git commit，可追溯 |
| PID 锁 | 防多开，同一时刻只有一个守护进程实例 |
| 看门狗 | 进程崩溃后 30 秒自动重启 |

---

## 📡 24/7 守护架构

```
开机自启 → ThinkingDaemon.bat
              ↓
        watchdog.py (pythonw, 无窗口)
              ↓
        daemon_launcher.py (PID锁)
         ┌──────┼──────┐
         ▼      ▼      ▼
     思考线程  爬虫线程 交易线程
    (30分钟)  (2小时)  (10分钟)
```

---

## 🔮 发展路线

- [x] 自我扫描与好奇心系统
- [x] 自我修改引擎（安全+回滚）
- [x] 24/7 守护进程（看门狗+3线程）
- [x] 学习优先级与行动触发
- [x] 物理电脑操控（鼠标键盘）
- [x] 实时市场监控
- [x] AI 内容生产流水线
- [ ] 实盘交易执行（需 API key）
- [ ] 通义万相+剪映全自动视频制作
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
  <sub>星期八 · 自我思考AI · 正在进化中</sub>
</p>
