from db import query_scalar, query_db


def kid_count():
    return query_scalar("chore_schedule", "SELECT COUNT(*) FROM kids WHERE active = 1")


def chore_count():
    return query_scalar("chore_schedule", "SELECT COUNT(*) FROM chores WHERE active = 1")


def todays_assignments():
    return query_db("chore_schedule", """
        SELECT k.name AS kid_name, c.name AS chore_name,
               c.difficulty, a.status
        FROM assignments a
        JOIN kids k ON a.kid_id = k.id
        JOIN chores c ON a.chore_id = c.id
        WHERE a.assigned_date = date('now')
        ORDER BY k.name, c.name
    """)


def weekly_completion_rates():
    return query_db("chore_schedule", """
        SELECT k.name,
               SUM(CASE WHEN a.status = 'done' THEN 1 ELSE 0 END) AS done,
               COUNT(*) AS total,
               ROUND(SUM(CASE WHEN a.status = 'done' THEN 1.0 ELSE 0 END)
                     / COUNT(*) * 100, 1) AS pct
        FROM assignments a
        JOIN kids k ON a.kid_id = k.id
        WHERE a.assigned_date >= date('now', 'weekday 1', '-7 days')
          AND a.assigned_date <= date('now')
        GROUP BY k.id
        ORDER BY k.name
    """)


def pending_count_today():
    return query_scalar("chore_schedule", """
        SELECT COUNT(*) FROM assignments
        WHERE status = 'pending' AND assigned_date = date('now')
    """)


def recent_completions(limit=10):
    return query_db("chore_schedule", """
        SELECT c.name AS chore_name, k.name AS kid_name, a.completed_at
        FROM assignments a
        JOIN kids k ON a.kid_id = k.id
        JOIN chores c ON a.chore_id = c.id
        WHERE a.status = 'done'
        ORDER BY a.completed_at DESC
        LIMIT ?
    """, (limit,))
