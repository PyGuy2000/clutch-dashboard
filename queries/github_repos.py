from db import query_db, query_scalar


def all_saved_repos():
    """All third-party repos saved for review, newest first."""
    return query_db("github_repos", """
        SELECT id, url, owner, name, description, reason,
               tags, priority, status, added_date, updated_at
        FROM repos
        ORDER BY created_at DESC
    """)


def saved_repo_count():
    return query_scalar("github_repos", "SELECT COUNT(*) FROM repos")


def repos_by_status():
    """Count of repos grouped by status."""
    return query_db("github_repos", """
        SELECT status, COUNT(*) as count
        FROM repos
        GROUP BY status
        ORDER BY count DESC
    """)
