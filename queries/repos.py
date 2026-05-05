from db import query_db, query_scalar


def all_repos():
    """All registered repos with milestone counts."""
    return query_db("content_ideas", """
        SELECT r.id, r.name, r.github_repo, r.live_url,
               r.domains, r.demonstrates, r.stack,
               r.last_commit_sha, r.last_commit_date,
               r.total_showcases, r.updated_at,
               COUNT(m.id) as milestone_count
        FROM project_registry r
        LEFT JOIN project_milestones m ON m.project_id = r.id
        GROUP BY r.id
        ORDER BY r.name
    """)


def repo_count():
    return query_scalar("content_ideas", "SELECT COUNT(*) FROM project_registry")


def milestone_count():
    return query_scalar("content_ideas", "SELECT COUNT(*) FROM project_milestones")
