#!/usr/bin/env python3
"""
🎯 搜索自适应AI项目
搜索具有主动适应、自我分析、主动沟通、自我提升功能的AI项目
"""

import requests
import json
from pathlib import Path
import datetime


def search_adaptive_ai_projects():
    """搜索自适应、自我学习的AI项目"""
    print("🔍 正在搜索自适应AI项目...")

    search_terms = [
        "self-adaptive ai", "adaptive ai system",
        "self-learning ai", "ai that learns",
        "self-improving ai", "ai that improves itself",
        "self-aware ai assistant", "adaptive learning system",
        "ai personality system", "ai communication system"
    ]

    projects = []

    for term in search_terms:
        try:
            # GitHub API搜索
            url = f"https://api.github.com/search/repositories?q={term}&sort=stars&order=desc&per_page=3"
            headers = {"Accept": "application/vnd.github.v3+json"}

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for repo in data["items"]:
                    project_info = {
                        "name": repo["name"],
                        "description": repo["description"],
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"],
                        "language": repo["language"],
                        "url": repo["html_url"],
                        "search_term": term
                    }
                    projects.append(project_info)
                    print(f"✅ 找到项目: {repo['name']} ({repo['stargazers_count']} stars)")

        except Exception as e:
            print(f"⚠️  搜索 '{term}' 失败: {e}")
            continue

        import time
        time.sleep(1)

    return projects


def search_ai_communication_projects():
    """搜索AI沟通系统项目"""
    print("\n🔍 正在搜索AI沟通系统项目...")

    communication_terms = [
        "ai communication system", "ai interaction system",
        "ai personality system", "emotional ai system",
        "adaptive ai interface", "ai that talks"
    ]

    projects = []

    for term in communication_terms:
        try:
            url = f"https://api.github.com/search/repositories?q={term}&sort=stars&order=desc&per_page=3"
            headers = {"Accept": "application/vnd.github.v3+json"}

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for repo in data["items"]:
                    project_info = {
                        "name": repo["name"],
                        "description": repo["description"],
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"],
                        "language": repo["language"],
                        "url": repo["html_url"],
                        "search_term": term
                    }
                    projects.append(project_info)
                    print(f"✅ 找到项目: {repo['name']} ({repo['stargazers_count']} stars)")

        except Exception as e:
            print(f"⚠️  搜索 '{term}' 失败: {e}")
            continue

        import time
        time.sleep(1)

    return projects


def analyze_projects(projects):
    """分析项目特性"""
    print("\n📊 项目特性分析:")

    language_count = {}
    star_ranges = {"0-100": 0, "100-1000": 0, "1000-5000": 0, "5000+": 0}
    features = {}

    for project in projects:
        lang = project.get("language", "Unknown")
        language_count[lang] = language_count.get(lang, 0) + 1

        stars = project["stars"]
        if stars < 100:
            star_ranges["0-100"] += 1
        elif stars < 1000:
            star_ranges["100-1000"] += 1
        elif stars < 5000:
            star_ranges["1000-5000"] += 1
        else:
            star_ranges["5000+"] += 1

        desc = (project["description"] or "").lower()
        if "adaptive" in desc or "self-adaptive" in desc:
            features["adaptive"] = features.get("adaptive", 0) + 1
        if "self-learning" in desc or "self-improving" in desc:
            features["self_learning"] = features.get("self_learning", 0) + 1
        if "communication" in desc or "interaction" in desc:
            features["communication"] = features.get("communication", 0) + 1
        if "personality" in desc or "emotional" in desc:
            features["emotional"] = features.get("emotional", 0) + 1

    print(f"\n语言分布:")
    for lang, count in language_count.items():
        print(f"  • {lang}: {count}个项目")

    print(f"\nStars分布:")
    for range_name, count in star_ranges.items():
        print(f"  • {range_name}: {count}个项目")

    print(f"\n功能特性:")
    for feature, count in features.items():
        feature_name = {
            "adaptive": "自适应",
            "self_learning": "自我学习",
            "communication": "沟通能力",
            "emotional": "情感特性"
        }.get(feature, feature)
        print(f"  • {feature_name}: {count}个项目")


def save_projects(projects):
    """保存项目数据"""
    output_dir = Path("adaptive_ai_projects")
    if not output_dir.exists():
        output_dir.mkdir()

    output_file = output_dir / "adaptive_ai_projects.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 项目数据已保存到: {output_file}")


def create_summary_report(projects):
    """创建项目分析报告"""
    report_file = Path("adaptive_ai_projects") / "project_summary.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# 🎯 自适应AI项目分析报告\n\n")
        f.write(f"**搜索时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**项目总数**: {len(projects)}\n\n")

        f.write("## 📊 项目特性分布\n\n")

        for project in projects:
            desc = (project["description"] or "").lower()
            features = []
            if "adaptive" in desc or "self-adaptive" in desc:
                features.append("自适应")
            if "self-learning" in desc or "self-improving" in desc:
                features.append("自我学习")
            if "communication" in desc or "interaction" in desc:
                features.append("沟通能力")
            if "personality" in desc or "emotional" in desc:
                features.append("情感特性")

            feature_text = ", ".join(features) if features else "未知"

            f.write(f"### {project['name']}\n")
            f.write(f"- **Stars**: {project['stars']:,}\n")
            f.write(f"- **Forks**: {project['forks']:,}\n")
            f.write(f"- **语言**: {project['language']}\n")
            f.write(f"- **功能**: {feature_text}\n")
            f.write(f"- **链接**: {project['url']}\n")
            f.write(f"- **描述**: {project['description']}\n\n")

        f.write("## 💡 推荐项目\n\n")
        top_projects = sorted(projects, key=lambda x: x["stars"], reverse=True)[:5]
        for i, project in enumerate(top_projects, 1):
            f.write(f"### {i}. {project['name']}\n")
            f.write(f"- **Stars**: {project['stars']:,}\n")
            f.write(f"- **描述**: {project['description']}\n")
            f.write(f"- **链接**: {project['url']}\n\n")

    print(f"✅ 分析报告已生成: {report_file}")


def main():
    """主函数"""
    print("🎯 搜索自适应AI项目")
    print("=" * 60)

    projects = []

    adaptive_projects = search_adaptive_ai_projects()
    projects.extend(adaptive_projects)

    communication_projects = search_ai_communication_projects()
    projects.extend(communication_projects)

    seen = set()
    unique_projects = []
    for project in projects:
        if project["url"] not in seen:
            seen.add(project["url"])
            unique_projects.append(project)

    print(f"\n📋 总项目数: {len(unique_projects)}个")

    if unique_projects:
        analyze_projects(unique_projects)
        save_projects(unique_projects)
        create_summary_report(unique_projects)

        print(f"\n🎉 搜索完成！找到 {len(unique_projects)} 个符合条件的项目")
    else:
        print("\n⚠️  未找到符合条件的项目")


if __name__ == "__main__":
    main()