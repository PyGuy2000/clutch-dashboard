from db import query_db, query_scalar


def all_jobs_summary():
    """All jobs with last run info, 7-day success rate, and failure count."""
    return query_db("cron_log", """
        SELECT
            job_name,
            MAX(started_at) as last_run,
            (SELECT status FROM cron_runs cr2
             WHERE cr2.job_name = cr.job_name
             ORDER BY started_at DESC LIMIT 1) as last_status,
            (SELECT duration_seconds FROM cron_runs cr3
             WHERE cr3.job_name = cr.job_name
             ORDER BY started_at DESC LIMIT 1) as last_duration,
            COUNT(*) as runs_7d,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failures_7d,
            ROUND(
                (COUNT(*) - SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END)) * 100.0 / COUNT(*),
                1
            ) as success_rate_7d
        FROM cron_runs cr
        WHERE started_at >= datetime('now', '-7 days')
        GROUP BY job_name
        ORDER BY job_name
    """)


def stale_jobs(threshold_minutes=30):
    """Jobs that started but haven't completed in over N minutes."""
    return query_db("cron_log", """
        SELECT job_name, started_at, duration_seconds FROM cron_runs
        WHERE status = 'running'
          AND started_at <= datetime('now', '-{} minutes')
        ORDER BY started_at
    """.format(threshold_minutes))


def job_runs(job_name, limit=50):
    """Recent run history for a specific job."""
    return query_db("cron_log", """
        SELECT started_at, status, duration_seconds, error_message
        FROM cron_runs
        WHERE job_name = ?
        ORDER BY started_at DESC
        LIMIT ?
    """, (job_name, limit))


def job_duration_history(job_name, days=14):
    """Duration time series for Chart.js."""
    return query_db("cron_log", """
        SELECT started_at, duration_seconds
        FROM cron_runs
        WHERE job_name = ? AND status = 'success'
          AND started_at >= datetime('now', '-{} days')
        ORDER BY started_at
    """.format(days), (job_name,))


def total_jobs_count():
    return query_scalar("cron_log", """
        SELECT COUNT(DISTINCT job_name) FROM cron_runs
    """)
