from db import query_db, query_scalar


def daily_spend(days=30):
    """Daily spend for the last N days."""
    return query_db("usage_tracking", """
        SELECT date(timestamp) as day, SUM(estimated_cost) as total_cost
        FROM usage_log
        WHERE date(timestamp) >= date('now', '-{} days')
        GROUP BY date(timestamp)
        ORDER BY day
    """.format(days))


def model_breakdown(days=30):
    """Spend breakdown by model."""
    return query_db("usage_tracking", """
        SELECT model, SUM(estimated_cost) as total_cost, COUNT(*) as call_count
        FROM usage_log
        WHERE date(timestamp) >= date('now', '-{} days')
        GROUP BY model
        ORDER BY total_cost DESC
    """.format(days))


def skill_breakdown(days=30):
    """Spend breakdown by skill."""
    return query_db("usage_tracking", """
        SELECT skill, SUM(estimated_cost) as total_cost, COUNT(*) as call_count
        FROM usage_log
        WHERE date(timestamp) >= date('now', '-{} days')
        GROUP BY skill
        ORDER BY total_cost DESC
    """.format(days))


def monthly_projection():
    """Project monthly spend based on last 7 days average."""
    avg_daily = query_scalar("usage_tracking", """
        SELECT AVG(daily_total) FROM (
            SELECT SUM(estimated_cost) as daily_total
            FROM usage_log
            WHERE date(timestamp) >= date('now', '-7 days')
            GROUP BY date(timestamp)
        )
    """, default=0.0)
    return round(avg_daily * 30, 2)


def active_alerts():
    """Unresolved cost alerts."""
    return query_db("usage_tracking", """
        SELECT alert_type, message, threshold, actual_value, created_at
        FROM cost_alerts
        WHERE resolved = 0
        ORDER BY created_at DESC
    """)


def total_spend_month():
    """Total spend this calendar month."""
    return query_scalar("usage_tracking", """
        SELECT COALESCE(SUM(estimated_cost), 0) FROM usage_log
        WHERE strftime('%Y-%m', timestamp) = strftime('%Y-%m', 'now')
    """, default=0.0)
