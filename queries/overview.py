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


def twitter_trending():
    count = query_scalar("twitter_trends", """
        SELECT COUNT(*) FROM themes WHERE status = 'trending'
    """)
    cross = query_scalar("twitter_trends", """
        SELECT COUNT(*) FROM cross_source_themes WHERE correlation_score >= 0.3
    """)
    return {"trending": count, "cross_source": cross}


def chores_today():
    pending = query_scalar("chore_schedule", """
        SELECT COUNT(*) FROM assignments
        WHERE assigned_date = date('now') AND status = 'pending'
    """)
    done = query_scalar("chore_schedule", """
        SELECT COUNT(*) FROM assignments
        WHERE assigned_date = date('now') AND status = 'done'
    """)
    return {"pending": pending, "done": done, "total": pending + done}


def meal_plan_status():
    row = query_db("meal_planning", """
        SELECT status, id FROM meal_plans
        WHERE status IN ('active', 'draft')
        ORDER BY CASE status WHEN 'active' THEN 1 WHEN 'draft' THEN 2 END
        LIMIT 1
    """, one=True)
    dinner = None
    if row and row.get("id"):
        dinner_row = query_db("meal_planning", """
            SELECT COALESCE(r.name, pm.freetext_meal) AS meal_name
            FROM planned_meals pm
            LEFT JOIN recipes r ON pm.recipe_id = r.id
            WHERE pm.plan_id = ?
              AND pm.meal_type = 'dinner'
              AND pm.day_of_week = CASE CAST(strftime('%w', 'now') AS INTEGER)
                  WHEN 0 THEN 7 ELSE CAST(strftime('%w', 'now') AS INTEGER) END
            LIMIT 1
        """, (row["id"],), one=True)
        if dinner_row:
            dinner = dinner_row.get("meal_name")
    return {"status": row.get("status") if row else None, "dinner": dinner}


def active_projects():
    count = query_scalar("projecthub", """
        SELECT COUNT(*) FROM projects WHERE status = 'active'
    """)
    overdue = query_scalar("projecthub", """
        SELECT COUNT(*) FROM milestones
        WHERE target_date < date('now') AND completed_date IS NULL
    """)
    return {"active": count, "overdue": overdue}


def crm_summary():
    contacts = query_scalar("crm", "SELECT COUNT(*) FROM contacts")
    high_value = query_scalar("crm", """
        SELECT COUNT(*) FROM relationship_scores WHERE total_score >= 70
    """)
    stale = query_scalar("crm", """
        SELECT COUNT(*) FROM relationship_scores
        WHERE (total_score >= 70 AND days_since_contact >= 14)
           OR (total_score >= 50 AND days_since_contact >= 30)
    """)
    pipeline_value = query_scalar("crm", """
        SELECT COALESCE(SUM(amount), 0) FROM deals
        WHERE deal_stage NOT IN ('closedwon', 'closedlost')
    """, default=0.0)
    return {
        "contacts": contacts,
        "high_value": high_value,
        "stale": stale,
        "pipeline_value": pipeline_value,
    }
