from db import query_scalar, query_db


def cron_success_rate_24h():
    total = query_scalar("cron_log", """
        SELECT COUNT(*) FROM cron_runs
        WHERE started_at >= datetime('now', '-24 hours')
    """)
    if total == 0:
        return {"rate": 0, "total": 0, "failed": 0}
    failed = query_scalar("cron_log", """
        SELECT COUNT(*) FROM cron_runs
        WHERE started_at >= datetime('now', '-24 hours') AND status = 'failure'
    """)
    rate = round(((total - failed) / total) * 100, 1)
    return {"rate": rate, "total": total, "failed": failed}


def todays_cost():
    cost = query_scalar("usage_tracking", """
        SELECT COALESCE(SUM(cost_usd), 0) FROM usage_log
        WHERE date(timestamp) = date('now')
    """, default=0.0)
    alerts = query_db("usage_tracking", """
        SELECT * FROM cost_alerts
        WHERE acknowledged = 0
        ORDER BY created_at DESC LIMIT 3
    """)
    return {"cost": round(cost, 4), "active_alerts": len(alerts)}


def content_pipeline_counts():
    rows = query_db("content_ideas", """
        SELECT status, COUNT(*) as cnt FROM content_ideas
        GROUP BY status
    """)
    counts = {r["status"]: r["cnt"] for r in rows}
    return counts


def kb_stats():
    sources = query_scalar("knowledge_base", "SELECT COUNT(*) FROM sources")
    chunks = query_scalar("knowledge_base", "SELECT COUNT(*) FROM chunks")
    return {"sources": sources, "chunks": chunks, "flagged": 0}


def latest_briefing():
    row = query_db("briefings", """
        SELECT momentum_weekly, theme, created_at FROM briefings
        WHERE theme IS NOT NULL
        ORDER BY created_at DESC LIMIT 1
    """, one=True)
    return row


def high_match_jobs():
    count = query_scalar("job_market", """
        SELECT COUNT(*) FROM job_scores
        WHERE match_score >= 80 AND date(created_at) >= date('now', '-7 days')
    """)
    return count


def youtube_trending():
    count = query_scalar("youtube_channels", """
        SELECT COUNT(DISTINCT phrase) FROM phrases
        WHERE date(created_at) >= date('now', '-7 days')
    """)
    return count


def active_projects():
    count = query_scalar("projecthub", """
        SELECT COUNT(*) FROM projects WHERE status = 'active'
    """)
    overdue = query_scalar("projecthub", """
        SELECT COUNT(*) FROM milestones
        WHERE due_date < date('now') AND completed_at IS NULL
    """)
    return {"active": count, "overdue": overdue}
