from db import query_db, query_scalar


def all_projects():
    """All projects with summary info."""
    return query_db("projecthub", """
        SELECT
            id, name, classification, status, health_score,
            progress_percentage, tech_stack, updated_at, description
        FROM projects
        WHERE archived_at IS NULL
        ORDER BY
            CASE status
                WHEN 'active' THEN 1
                WHEN 'on_hold' THEN 2
                WHEN 'not_started' THEN 3
                WHEN 'completed' THEN 4
                ELSE 5
            END,
            updated_at DESC
    """)


def project_detail(project_id):
    """Single project by ID."""
    return query_db("projecthub", """
        SELECT * FROM projects WHERE id = ?
    """, (project_id,), one=True)


def project_milestones(project_id):
    """Milestones for a project."""
    return query_db("projecthub", """
        SELECT title, target_date, completed_date, status
        FROM milestones
        WHERE project_id = ?
        ORDER BY target_date
    """, (project_id,))


def project_time_entries(project_id, limit=20):
    """Recent time entries for a project."""
    return query_db("projecthub", """
        SELECT description, hours, date as logged_at
        FROM time_entries
        WHERE project_id = ?
        ORDER BY date DESC
        LIMIT ?
    """, (project_id, limit))


def summary_stats():
    """Active count, total hours this week, overdue milestones."""
    active = query_scalar("projecthub", """
        SELECT COUNT(*) FROM projects
        WHERE status = 'active' AND archived_at IS NULL
    """)
    hours_week = query_scalar("projecthub", """
        SELECT COALESCE(SUM(hours), 0) FROM time_entries
        WHERE date(date) >= date('now', '-7 days')
    """, default=0.0)
    overdue = query_scalar("projecthub", """
        SELECT COUNT(*) FROM milestones
        WHERE target_date < date('now') AND completed_date IS NULL
    """)
    return {"active": active, "hours_week": round(hours_week, 1), "overdue": overdue}
