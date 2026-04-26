from pathlib import Path
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DERIVED_DATA_DIR = DATA_DIR / "derived"
REPOS_JSON_PATH = RAW_DATA_DIR / "repos.json"
ANALYSIS_JSON_PATH = DERIVED_DATA_DIR / "analysis.json"

# --- Clustering Rules (based on previous analysis) ---
CLUSTER_RULES = {
    "A1. Assemble Pipeline": ["news-digest", "assemble-hunting", "assemble-processing", "assemble-archive", "assemble-publish", "assemble-publish-test"],
    "A2. Research Agent (Systematology)": ["Creating-Systematology-RAG", "Creating-Systematology", "Creating-Systematology-Test", "Creating-Systematology-Batch"],
    "A3. AI/Agent Infra": ["CloneX", "qiao-skills", "ocr-mcp-service", "agent-nightshift"],
    "A4. Personal System": ["One-Note", "personal-system-lab", "Inspiration"],
    "A5. Tech Learning": ["rust-rush", "Go-LearnCases", "Practice-Go-by-Example-", "Peters-Go-Day-Practice", "Java-Ecosystem", "learn-rocketmq-by-cursor", "Elasticsearch-In-Action-Ref-Code", "Strategy-pattern-demo"],
    "A6. Personal Content": ["Extensive-Intensive-Reading", "start-with-drifting", "Resume", "qiao-925", "cinnamon-backup-restore"],
}

def get_cluster(repo_name, is_fork=False):
    for cluster, names in CLUSTER_RULES.items():
        if repo_name in names:
            return cluster
    return "B. Learning Forks" if is_fork else "Z. Unclassified"

def get_activity_status(pushed_at_str):
    if not pushed_at_str:
        return "unknown"
    pushed_at = datetime.fromisoformat(pushed_at_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    delta = now - pushed_at

    if delta < timedelta(days=30):
        return "active"
    if delta < timedelta(days=180):
        return "stale"
    return "zombie"

def build_repository_record(repo: dict) -> dict:
    repo_name = repo.get("name", "")
    pushed_at = repo.get("pushedAt")
    is_fork = repo.get("isFork", False)
    activity = get_activity_status(pushed_at)

    return {
        "name": repo_name,
        "description": repo.get("description"),
        "url": f"https://github.com/qiao-925/{repo_name}",
        "is_fork": is_fork,
        "parent": (repo.get("parent") or {}).get("nameWithOwner", ""),
        "language": (repo.get("primaryLanguage") or {}).get("name"),
        "stars": repo.get("stargazerCount"),
        "pushed_at": pushed_at,
        "cluster": get_cluster(repo_name, is_fork=is_fork),
        "activity": activity,
    }


def build_action_items_for_repo(repo: dict) -> list[dict]:
    repo_name = repo.get("name", "")
    pushed_at = repo.get("pushedAt")
    is_fork = repo.get("isFork", False)
    disk_usage = repo.get("diskUsage", 0)
    activity = get_activity_status(pushed_at)
    cluster = get_cluster(repo_name, is_fork=is_fork)

    action_items = []
    if not is_fork and cluster not in ["A5. Tech Learning", "A6. Personal Content"] and disk_usage < 5:
        action_items.append({
            "priority": "P1",
            "title": "核心项目待实现",
            "description": f"核心项目 '{repo_name}' 几乎为空，需填充实现。",
            "repo_name": repo_name,
        })
    if not is_fork and activity == "zombie":
        action_items.append({
            "priority": "P2",
            "title": "审查陈旧的主仓库",
            "description": f"主仓库 '{repo_name}' 已超过6个月未更新，建议审查或归档。",
            "repo_name": repo_name,
        })
    if is_fork and pushed_at and activity == 'zombie' and (datetime.now(timezone.utc) - datetime.fromisoformat(pushed_at.replace("Z", "+00:00")) > timedelta(days=365)):
        action_items.append({
            "priority": "P3",
            "title": "清理陈旧的 Fork",
            "description": f"Fork 仓库 '{repo_name}' 已超过1年未更新，建议清理。",
            "repo_name": repo_name,
        })

    return action_items


def build_timeline(repos: list[dict]) -> list[tuple[str, int]]:
    timeline_data = defaultdict(int)
    for repo in repos:
        if repo.get("isFork"):
            continue
        created_at = repo.get("createdAt")
        if created_at:
            timeline_data[created_at[:7]] += 1

    return sorted(timeline_data.items())


def build_summary(repos: list[dict], analyzed_repos: list[dict]) -> dict:
    return {
        "total_repos": len(repos),
        "active_repos": sum(1 for r in analyzed_repos if r['activity'] == 'active'),
        "source_repos": sum(1 for r in repos if not r['isFork']),
        "fork_repos": sum(1 for r in repos if r['isFork']),
    }


def build_output_data(repos: list[dict]) -> dict:
    analyzed_repos = [build_repository_record(repo) for repo in repos]
    action_items = []
    for repo in repos:
        action_items.extend(build_action_items_for_repo(repo))

    activity_order = {"active": 0, "stale": 1, "zombie": 2, "unknown": 3}
    analyzed_repos.sort(key=lambda x: (x["cluster"], activity_order.get(x["activity"], 99), x["pushed_at"] or ""))
    action_items.sort(key=lambda x: x["priority"])

    return {
        "repositories": analyzed_repos,
        "action_items": action_items,
        "timeline": build_timeline(repos),
        "summary": build_summary(repos, analyzed_repos),
    }


def load_repositories() -> list[dict]:
    if not REPOS_JSON_PATH.exists():
        print(f"Error: {REPOS_JSON_PATH} not found. Please run fetch_repos.py first.")
        raise SystemExit(1)

    with open(REPOS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def write_analysis(output_data: dict) -> None:
    with open(ANALYSIS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)


def main() -> None:
    """Analyzes repository data, assigning clusters and activity status."""
    DERIVED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    repos = load_repositories()
    output_data = build_output_data(repos)
    write_analysis(output_data)

    print(f"Analysis complete. {len(output_data['repositories'])} repositories analyzed. {len(output_data['action_items'])} action items generated.")
    print(f"Results saved to {ANALYSIS_JSON_PATH}")


if __name__ == "__main__":
    main()
