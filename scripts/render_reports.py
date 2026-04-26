from html import escape
from pathlib import Path
import json
from collections import defaultdict

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
DERIVED_DATA_DIR = DATA_DIR / "derived"
ANALYSIS_JSON_PATH = DERIVED_DATA_DIR / "analysis.json"
DASHBOARD_HTML_PATH = ROOT_DIR / "dashboard.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Repo Atlas Dashboard</title>
    <style>
        :root {{
            --bg: #f7f3ee;
            --surface: #fffaf6;
            --surface-elevated: #ffffff;
            --text: #2f241f;
            --muted: #7c6a5f;
            --border: #eadfd6;
            --accent: #c46a3b;
            --accent-soft: #f4e3d8;
            --shadow: 0 10px 30px rgba(84, 53, 35, 0.08);
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            background: linear-gradient(180deg, #fbf8f4 0%, var(--bg) 100%);
            color: var(--text);
            font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
        }}
        a {{ color: var(--accent); }}
        .container {{ max-width: 1120px; margin: 0 auto; padding: 48px 24px 64px; }}
        .header {{
            background: rgba(255, 250, 246, 0.9);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 32px 28px;
            box-shadow: var(--shadow);
            margin-bottom: 28px;
        }}
        h1 {{ font-size: clamp(2rem, 4vw, 3.2rem); margin: 0 0 8px; letter-spacing: -0.03em; }}
        .header p {{ margin: 0; color: var(--muted); font-size: 1.05rem; }}
        h2 {{
            font-size: 1.35rem;
            margin: 0 0 16px;
            letter-spacing: -0.02em;
            color: var(--text);
        }}
        .section {{
            background: rgba(255, 250, 246, 0.85);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 24px;
            box-shadow: var(--shadow);
            margin-top: 24px;
        }}
        .cluster {{ margin-bottom: 22px; }}
        .repo-table {{ width: 100%; border-collapse: collapse; overflow: hidden; border-radius: 16px; }}
        .repo-table th, .repo-table td {{ text-align: left; padding: 14px 16px; border-bottom: 1px solid var(--border); vertical-align: top; }}
        .repo-table th {{ background: #f7eee6; color: var(--muted); font-size: 0.86rem; text-transform: uppercase; letter-spacing: 0.06em; }}
        .repo-table tr:hover td {{ background: #fffdfb; }}
        .repo-name a {{ color: var(--text); text-decoration: none; font-weight: 650; }}
        .repo-name a:hover {{ color: var(--accent); }}
        .status-active {{ color: #2d8a57; font-weight: 600; }}
        .status-stale {{ color: #b7791f; font-weight: 600; }}
        .status-zombie {{ color: #8c7a6b; font-weight: 600; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 18px; }}
        .summary-item {{ background: var(--surface-elevated); padding: 22px; border-radius: 18px; border: 1px solid var(--border); box-shadow: var(--shadow); }}
        .summary-item .value {{ font-size: 2.1rem; font-weight: 700; letter-spacing: -0.03em; color: var(--accent); }}
        .summary-item .label {{ font-size: 0.9rem; color: var(--muted); margin-top: 4px; }}
        .eyebrow {{
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            background: var(--accent-soft);
            color: var(--accent);
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="eyebrow">Claude-style overview</div>
            <h1>Repo Atlas Dashboard</h1>
            <p>A calm, editorial snapshot of the qiao-925 GitHub account.</p>
        </div>
        <div class="summary-grid">
            {summary_section}
        </div>
        {action_items_section}
        {timeline_section}
        {clusters_section}
    </div>
</body>
</html>
"""

def load_analysis_data() -> dict:
    if not ANALYSIS_JSON_PATH.exists():
        print(f"Error: {ANALYSIS_JSON_PATH} not found. Please run analyze_portfolio.py first.")
        raise SystemExit(1)

    with open(ANALYSIS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_summary_section(summary: dict) -> str:
    return f"""
        <div class="summary-item"><div class="value">{summary.get('total_repos', 0)}</div><div class="label">Total Repos</div></div>
        <div class="summary-item"><div class="value">{summary.get('active_repos', 0)}</div><div class="label">Active (30d)</div></div>
        <div class="summary-item"><div class="value">{summary.get('source_repos', 0)}</div><div class="label">Source Repos</div></div>
        <div class="summary-item"><div class="value">{summary.get('fork_repos', 0)}</div><div class="label">Forks</div></div>
    """


def build_action_items_section(action_items: list[dict]) -> str:
    if not action_items:
        return ""

    section_html = '<section class="section"><h2>Action Priority Suggestions</h2><table class="repo-table">'
    section_html += '<tr><th>Priority</th><th>Suggestion</th><th>Repository</th></tr>'
    for item in action_items:
        repo_name = escape(item['repo_name'])
        description = escape(item['description'])
        section_html += f"""
            <tr>
                <td><strong>{escape(item['priority'])}</strong></td>
                <td>{description}</td>
                <td><a href="https://github.com/qiao-925/{repo_name}" target="_blank">{repo_name}</a></td>
            </tr>
            """
    section_html += '</table></section>'
    return section_html


def build_timeline_section(timeline: list[tuple[str, int]]) -> str:
    if not timeline:
        return ""

    section_html = '<section class="section"><h2>Evolution Timeline</h2><table class="repo-table">'
    section_html += '<tr><th>Month</th><th>New Source Repos</th></tr>'
    for month, count in timeline:
        section_html += f'<tr><td>{month}</td><td>{count}</td></tr>'
    section_html += '</table></section>'
    return section_html


def build_clusters_section(repos: list[dict]) -> str:
    clusters = defaultdict(list)
    for repo in repos:
        clusters[repo["cluster"]].append(repo)

    clusters_html = ""
    for cluster_name, cluster_repos in sorted(clusters.items()):
        clusters_html += f'\n<section class="section cluster">\n    <h2>{cluster_name} ({len(cluster_repos)})</h2>\n'
        clusters_html += '    <table class="repo-table">\n        <tr><th>Name</th><th>Description</th><th>Language</th><th>Activity</th></tr>\n'

        for repo in cluster_repos:
            repo_name = escape(repo.get("name", ""))
            description = repo.get("description", "") or ""
            lang = escape(repo.get("language", "-") or "-")
            activity = repo.get("activity", "unknown")
            activity_class = escape(activity)
            url = escape(repo.get("url", "#"))
            safe_description = escape(description[:80] + '...' if description and len(description) > 80 else description)

            clusters_html += f"""
            <tr>
                <td class="repo-name"><a href="{url}" target="_blank">{repo_name}</a></td>
                <td>{safe_description}</td>
                <td>{lang}</td>
                <td class="status-{activity_class}">{activity.capitalize()}</td>
            </tr>
            """
        clusters_html += '    </table>\n</section>'

    return clusters_html


def build_final_html(summary_section: str, action_items_section: str, timeline_section: str, clusters_section: str) -> str:
    return HTML_TEMPLATE.format(
        summary_section=summary_section,
        action_items_section=action_items_section,
        timeline_section=timeline_section,
        clusters_section=clusters_section,
    )


def write_dashboard(html: str) -> None:
    with open(DASHBOARD_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)


def main() -> None:
    """Renders the analysis results into a static HTML dashboard."""
    data = load_analysis_data()

    repos = data.get("repositories", [])
    action_items = data.get("action_items", [])
    timeline = data.get("timeline", [])
    summary = data.get("summary", {})

    summary_section = build_summary_section(summary)
    action_items_section = build_action_items_section(action_items)
    timeline_section = build_timeline_section(timeline)
    clusters_section = build_clusters_section(repos)
    final_html = build_final_html(summary_section, action_items_section, timeline_section, clusters_section)

    write_dashboard(final_html)

    print(f"Dashboard generated successfully.")
    print(f"You can now open {DASHBOARD_HTML_PATH} in your browser.")


if __name__ == "__main__":
    Path("data/reports").mkdir(parents=True, exist_ok=True)
    main()
