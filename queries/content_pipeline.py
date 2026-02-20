from db import query_db, query_scalar


def ideas_by_status():
    """Content ideas grouped by status."""
    return query_db("content_ideas", """
        SELECT id, title, status, post_type, source_type, created_at, updated_at
        FROM content_ideas
        ORDER BY
            CASE status
                WHEN 'published' THEN 4
                WHEN 'drafted' THEN 3
                WHEN 'approved' THEN 2
                WHEN 'pitched' THEN 1
                ELSE 5
            END,
            updated_at DESC
    """)


def publishing_pace_weekly(weeks=8):
    """Published posts per week for the last N weeks."""
    return query_db("content_ideas", """
        SELECT
            strftime('%Y-W%W', updated_at) as week,
            COUNT(*) as count
        FROM content_ideas
        WHERE status = 'published'
          AND updated_at >= date('now', '-{} days')
        GROUP BY week
        ORDER BY week
    """.format(weeks * 7))


def post_type_distribution():
    """Count of ideas by post type."""
    return query_db("content_ideas", """
        SELECT post_type, COUNT(*) as count
        FROM content_ideas
        GROUP BY post_type
        ORDER BY count DESC
    """)


def dedup_stats():
    """Deduplication statistics."""
    total = query_scalar("content_ideas", "SELECT COUNT(*) FROM content_ideas")
    duplicates = query_scalar("content_ideas", """
        SELECT COUNT(*) FROM content_ideas WHERE duplicate_of IS NOT NULL
    """)
    return {"total": total, "duplicates": duplicates}


def recent_activity(limit=10):
    """Recently updated content ideas."""
    return query_db("content_ideas", """
        SELECT title, status, post_type, updated_at
        FROM content_ideas
        ORDER BY updated_at DESC
        LIMIT ?
    """, (limit,))


def status_counts():
    """Count of ideas per status."""
    rows = query_db("content_ideas", """
        SELECT status, COUNT(*) as count FROM content_ideas GROUP BY status
    """)
    return {r["status"]: r["count"] for r in rows}
