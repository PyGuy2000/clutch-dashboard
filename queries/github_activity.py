from db import query_db, query_scalar


def activity_stats():
    """Summary stats for the GitHub Activity page."""
    total_repos = query_scalar("projecthub", """
        SELECT COUNT(DISTINCT github_repo) FROM github_activity
    """)
    commits_week = query_scalar("projecthub", """
        SELECT COUNT(*) FROM github_activity
        WHERE event_type = 'commit'
        AND event_date >= datetime('now', '-7 days')
    """)
    open_prs = query_scalar("projecthub", """
        SELECT COUNT(*) FROM github_activity
        WHERE event_type = 'pr_opened'
    """)
    active_repos_week = query_scalar("projecthub", """
        SELECT COUNT(DISTINCT github_repo) FROM github_activity
        WHERE event_type = 'commit'
        AND event_date >= datetime('now', '-7 days')
    """)
    return {
        "total_repos": total_repos,
        "commits_week": commits_week,
        "open_prs": open_prs,
        "active_repos_week": active_repos_week,
    }


def recent_commits(limit=50):
    """Most recent commits across all repos."""
    return query_db("projecthub", """
        SELECT
            ga.github_repo,
            ga.title,
            ga.author,
            ga.event_date,
            ga.url,
            p.name as project_name,
            p.id as project_id
        FROM github_activity ga
        LEFT JOIN projects p ON ga.project_id = p.id
        WHERE ga.event_type = 'commit'
        ORDER BY ga.event_date DESC
        LIMIT ?
    """, (limit,))


def open_pull_requests():
    """All currently open PRs."""
    return query_db("projecthub", """
        SELECT
            ga.github_repo,
            ga.title,
            ga.author,
            ga.event_date,
            ga.branch,
            ga.url,
            p.name as project_name,
            p.id as project_id
        FROM github_activity ga
        LEFT JOIN projects p ON ga.project_id = p.id
        WHERE ga.event_type = 'pr_opened'
        ORDER BY ga.event_date DESC
    """)


def recent_merged_prs(limit=20):
    """Recently merged PRs."""
    return query_db("projecthub", """
        SELECT
            ga.github_repo,
            ga.title,
            ga.author,
            ga.event_date,
            ga.branch,
            ga.url,
            p.name as project_name,
            p.id as project_id
        FROM github_activity ga
        LEFT JOIN projects p ON ga.project_id = p.id
        WHERE ga.event_type = 'pr_merged'
        ORDER BY ga.event_date DESC
        LIMIT ?
    """, (limit,))


def commits_per_repo_week():
    """Commits per repo in the last 7 days, for the chart."""
    return query_db("projecthub", """
        SELECT
            github_repo,
            COUNT(*) as commit_count,
            p.name as project_name
        FROM github_activity ga
        LEFT JOIN projects p ON ga.project_id = p.id
        WHERE ga.event_type = 'commit'
        AND ga.event_date >= datetime('now', '-7 days')
        GROUP BY ga.github_repo
        ORDER BY commit_count DESC
        LIMIT 15
    """)


def daily_commit_counts(days=30):
    """Commit counts per day for the last N days, for the activity chart."""
    return query_db("projecthub", """
        SELECT
            date(event_date) as day,
            COUNT(*) as commit_count
        FROM github_activity
        WHERE event_type = 'commit'
        AND event_date >= datetime('now', ? || ' days')
        GROUP BY date(event_date)
        ORDER BY day
    """, (f"-{days}",))


def repo_summary():
    """Per-repo summary: last commit, total commits, open PRs."""
    return query_db("projecthub", """
        SELECT
            ga.github_repo,
            p.name as project_name,
            p.id as project_id,
            MAX(CASE WHEN ga.event_type = 'commit' THEN ga.event_date END) as last_commit,
            SUM(CASE WHEN ga.event_type = 'commit' THEN 1 ELSE 0 END) as total_commits,
            SUM(CASE WHEN ga.event_type = 'pr_opened' THEN 1 ELSE 0 END) as open_prs,
            SUM(CASE WHEN ga.event_type = 'pr_merged' THEN 1 ELSE 0 END) as merged_prs,
            SUM(CASE WHEN ga.event_type = 'commit'
                AND ga.event_date >= datetime('now', '-7 days') THEN 1 ELSE 0 END) as commits_week
        FROM github_activity ga
        LEFT JOIN projects p ON ga.project_id = p.id
        GROUP BY ga.github_repo
        ORDER BY last_commit DESC
    """)
