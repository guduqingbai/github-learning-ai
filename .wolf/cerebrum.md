# Cerebrum

> OpenWolf's learning memory. Updated automatically as the AI learns from interactions.
> Do not edit manually unless correcting an error.
> Last updated: 2026-05-06

## User Preferences

<!-- How the user likes things done. Code style, tools, patterns, communication. -->

- **隐私:** 项目文件中不能出现真实姓名/用户名/个人路径。路径用相对路径或环境变量

## Key Learnings

- **Project:** github-learning (AI 自我思考系统)
- **SelfMemory 三层结构:** experiences → insights → narrative，情绪基于真实结果推导
- **CircuitBreaker 状态机:** CLOSED → OPEN(3次失败) → HALF_OPEN(120s冷却) → CLOSED/OPEN
- **AntibodyLibrary v3:** FixStrategy 多策略编排 + ProblemTriage(按 importance 决定策略数量) + Buglog(可搜索修复存档)
- **问题指纹去重:** 用 (file + issue_type + lineno) 的 MD5 指纹持久化到 seen_issues.json，避免每轮报同样问题
- **DESIGN.md 格式:** YAML frontmatter(colors/typography/rounded/spacing/components) + 9 板块 Markdown 描述。AI 前端设计规范标准格式
- **awesome-design-md:** 71 个品牌 DESIGN.md 收集库，`design-references/` 目录存储。当前默认 Stripe 风格

## Do-Not-Repeat

<!-- Mistakes made and corrected. Each entry prevents the same mistake recurring. -->
<!-- Format: [YYYY-MM-DD] Description of what went wrong and what to do instead. -->

- [2026-05-06] **探索绕过抗体**: daemon._apply_heals() 在探索全部失败时仍 continue 跳过抗体。修复: 检查 any_success，全部失败则继续走抗体策略
- [2026-05-06] **SelfMemory 只写不读**: 思考开始前未加载自我状态(情绪/经历/暂缓问题)。修复: _load_self_context() 在 _generate_questions() 前调用
- [2026-05-06] **扫描器无去重**: analyze_code_quality() 每轮报告全部 1292 个问题。修复: 按 (file+type+lineno) 生成 MD5 指纹，只报告新问题
- [2026-05-06] **宪法校验拦启动**: 修改 constitution 保护的文件后需手动 `store_checksums()`，否则 daemon 拒绝启动

## Key Learnings

- **AntibodyLibrary v3:** FixStrategy 多策略编排 + ProblemTriage(按 importance 决定策略数量) + Buglog(可搜索修复存档)
- **问题指纹去重:** 用 (file + issue_type + lineno) 的 MD5 指纹持久化到 seen_issues.json，避免每轮报同样问题
- **DESIGN.md 格式:** YAML frontmatter(colors/typography/rounded/spacing/components) + 9 板块 Markdown 描述。AI 前端设计规范标准格式
- **awesome-design-md:** 71 个品牌 DESIGN.md 收集库，`design-references/` 目录存储。当前默认 Stripe 风格
- **ModSubGates 模式:** 每个修改类型一个独立开关（allow_bare_except_fix / allow_docstring_add / allow_type_hints_add），在引擎和 daemon 两处配置
- **add_return_types 抗体:** 只对明确不返回值的函数添加 `-> None`（无 return / 仅 bare return），有值 return 或 yield 的跳过

## Do-Not-Repeat

## Decision Log

<!-- Significant technical decisions with rationale. Why X was chosen over Y. -->
