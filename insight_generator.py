"""
💡 洞察生成器 — 从探索结果生成结构化洞察
从 self_thinking_agent.py 抽出，纯函数模块
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


# ── 路由器 ──────────────────────────────────────

def generate_insight(q, exploration: Dict[str, Any]) -> Dict[str, Any]:
    """从探索结果生成洞察"""
    if "error" in exploration:
        return {
            "observation": q.observation,
            "question": q.question,
            "summary": f"探索失败: {exploration['error']}",
            "action_taken": "error",
            "exploration": exploration,
        }

    if q.explore_action == "read_file":
        return _insight_from_file(q, exploration)
    elif q.explore_action == "compare_files":
        return _insight_from_comparison(q, exploration)
    elif q.explore_action == "add_crawler_task":
        return _insight_from_gap(q, exploration)
    elif q.explore_action == "global_research":
        return _insight_from_global_research(q, exploration)
    elif q.explore_action in ("self_heal", "code_quality_heal"):
        return _insight_from_self_heal(q, exploration)
    elif q.explore_action == "deep_learning":
        return _insight_from_deep_learning(q, exploration)
    else:
        return {
            "observation": q.observation,
            "question": q.question,
            "summary": f"探索 {q.target} 完成",
            "exploration": exploration,
        }


# ── 各类型洞察生成器 ────────────────────────────

def _insight_from_file(q, exploration: Dict[str, Any]) -> Dict[str, Any]:
    """从文件探索生成洞察"""
    file = exploration.get("file", q.target)
    classes = exploration.get("classes", [])
    funcs = exploration.get("top_functions", [])
    imports = exploration.get("imports", [])
    doc = exploration.get("docstring", "")
    lines = exploration.get("lines", 0)

    parts = []
    if classes:
        class_desc = ", ".join(f"{c['name']}({len(c['methods'])}方法)" for c in classes[:5])
        parts.append(f"定义了 {len(classes)} 个类: {class_desc}")
    if funcs:
        parts.append(f"包含 {exploration.get('function_count', 0)} 个函数")
    if imports:
        parts.append(f"依赖 {exploration.get('import_count', 0)} 个外部模块")

    primary_purpose = doc[:100] if doc and doc != "(无模块文档)" else "模块文档缺失"
    summary = f"{file} ({lines}行): {primary_purpose}。{'; '.join(parts)}。"

    findings = []
    if doc == "(无模块文档)":
        findings.append("模块级文档缺失")

    return {
        "observation": q.observation,
        "question": q.question,
        "summary": summary,
        "topic": f"{file.replace('.py', '')} 模块分析",
        "category": "项目自身",
        "content": f"{summary}\n\n结构:\n- 类: {json.dumps(classes, ensure_ascii=False)}\n- 主要函数: {funcs}\n- imports: {imports}",
        "keywords": [file.replace(".py", ""), "模块分析"] +
                    ([c["name"] for c in classes[:3]] if classes else []),
        "findings": findings,
        "origin": "self_thinking",
    }


def _insight_from_comparison(q, exploration: Dict[str, Any]) -> Dict[str, Any]:
    s = exploration.get("jaccard_similarity", 0)
    a = exploration.get("file_a", "")
    b = exploration.get("file_b", "")
    conclusion = exploration.get("conclusion", "")

    summary = f"对比 {a} 和 {b}: import 相似度 {s:.0%}，{conclusion}。"

    return {
        "observation": q.observation,
        "question": q.question,
        "summary": summary,
        "topic": f"{a} vs {b} 相似度分析",
        "category": "项目自身",
        "content": summary,
        "keywords": [a.replace(".py", ""), b.replace(".py", ""), "相似度分析"],
        "findings": [],
        "origin": "self_thinking",
    }


def _insight_from_gap(q, exploration: Dict[str, Any]) -> Dict[str, Any]:
    domain = exploration.get("domain", q.target)
    missing = exploration.get("missing_topics", [])

    summary = f"发现知识缺口: {domain} 领域缺 {len(missing)} 个子话题，已生成爬虫任务。"

    return {
        "observation": q.observation,
        "question": q.question,
        "summary": summary,
        "topic": f"知识缺口: {domain}",
        "category": "项目自身",
        "content": f"领域 {domain} 缺少以下知识: {', '.join(missing)}。已生成定向爬虫任务。",
        "keywords": [domain, "知识缺口"],
        "findings": [f"缺失 {len(missing)} 个话题"],
        "origin": "self_thinking",
        "action_taken": "add_crawler_tasks",
    }


def _insight_from_global_research(q, exploration: Dict[str, Any]) -> Dict[str, Any]:
    topic = exploration.get("research_topic", "global")
    results = exploration.get("sample_results", [])
    tasks = exploration.get("crawler_tasks_added", 0)
    realtime = exploration.get("real_time_results", 0)

    top_results = ""
    for r in results[:3]:
        top_results += f"- [{r['source']}] {r['title']} ({r.get('stars', 0)}⭐) {r.get('description', '')[:80]}\n"

    summary = f"全球研究 [{topic}]: 已调度 {tasks} 个爬虫任务"
    if results:
        summary += f"，实时获取 {len(results)} 条结果\n{top_results[:200]}"

    content = (
        f"好奇心驱动全球研究: {q.question}\n\n"
        f"搜索查询:\n"
        + "\n".join(f"- {qq}" for qq in q.context.get("research_queries", []))
        + f"\n\n实时结果:\n{top_results}"
        + f"\n爬虫将持续在后台上获取更多资料。"
    )

    return {
        "observation": q.observation,
        "question": q.question,
        "summary": summary,
        "topic": f"全球研究: {topic}",
        "category": "项目自身",
        "content": content,
        "keywords": [topic, "全球研究", "架构探索"],
        "findings": [f"调度了 {tasks} 个爬虫任务", f"实时获取 {realtime} 条结果"],
        "origin": "self_thinking",
        "action_taken": "global_research",
    }


def _insight_from_self_heal(q, exploration: Dict[str, Any]) -> Dict[str, Any]:
    target = exploration.get("target", q.target)
    attempted = exploration.get("fixes_attempted", 0)
    succeeded = exploration.get("fixes_succeeded", 0)
    fix_results = exploration.get("fix_results", [])

    detail_lines = []
    for fix in fix_results:
        status = "✅" if fix["success"] else "❌"
        detail_lines.append(f"  {status} [{fix['type']}] {fix['file']}: {fix['detail']}")

    summary = f"自我修复 [{target}]: 尝试 {attempted} 项修复，成功 {succeeded} 项\n" + "\n".join(detail_lines)

    base_finding = f"修复 {succeeded}/{attempted} 项" if attempted > 0 else "无需修复"
    issue_keywords = []
    if "裸 except" in q.question or "bare except" in q.question.lower():
        issue_keywords.append("裸 except")
    if "文档" in q.question or "docstring" in q.question.lower():
        issue_keywords.append("文档缺失")
    if "类型" in q.question or "type hint" in q.question.lower():
        issue_keywords.append("类型提示")
    findings = [base_finding] + issue_keywords

    return {
        "observation": q.observation,
        "question": q.question,
        "summary": summary,
        "topic": f"{Path(target).stem} 自我修复",
        "category": "项目自身",
        "content": f"好奇心引擎发现代码问题并自动修复:\n\n问题: {q.question}\n观察: {q.observation}\n\n修复结果:\n" + "\n".join(detail_lines),
        "keywords": [Path(target).stem, "自我修复", "代码质量"],
        "findings": findings,
        "origin": "self_thinking",
        "action_taken": "self_heal",
        "modification_proposal": {
            "file": target,
            "fixes": fix_results,
            "auto_applied": succeeded > 0,
        },
    }


def _insight_from_deep_learning(q, exploration: Dict[str, Any]) -> Dict[str, Any]:
    missing = exploration.get("missing_capabilities", [])
    topic = exploration.get("topic", q.target)
    return {
        "observation": q.observation,
        "question": q.question,
        "summary": exploration.get("summary", f"能力深度探索 [{topic}]"),
        "topic": f"能力深度: {topic}",
        "category": "能力参考",
        "content": exploration.get("summary", ""),
        "keywords": [topic] + missing[:5],
        "findings": missing[:5],
        "origin": "capability_audit",
        "action_taken": "deep_learning",
    }


# ── 存储 ────────────────────────────────────────

def store_insight(insight: Dict[str, Any]) -> bool:
    """将洞察存入知识库"""
    try:
        from knowledge_base import KnowledgeBase
        kb = KnowledgeBase()

        topic = insight.get("topic", "")
        if not topic:
            return False

        existing = kb.get_all_knowledge()
        if any(item.get("topic") == topic for item in existing):
            return False

        entry = {
            "topic": topic,
            "category": insight.get("category", "项目自身"),
            "content": insight.get("content", insight.get("summary", "")),
            "source": "自我思考",
            "keywords": insight.get("keywords", []),
            "references": [],
            "importance": 0.9,
            "learning_time": datetime.now().isoformat(),
        }
        return kb.add_knowledge(entry)
    except Exception as e:
        print(f"⚠️  知识库存储失败: {e}")
        return False
