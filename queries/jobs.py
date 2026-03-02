import json

from db import query_db, query_scalar


def _format_json_list(raw):
    """Parse JSON array of [name, count] pairs into 'name (count), ...' string."""
    if not raw:
        return None
    try:
        items = json.loads(raw)
        return ", ".join(f"{name} ({count})" for name, count in items)
    except (json.JSONDecodeError, TypeError, ValueError):
        return raw


def high_match_jobs(min_score=70):
    """Jobs above score threshold."""
    return query_db("job_market", """
        SELECT job_title, company, location, work_type, experience_level,
               match_score, skill_match, experience_match, opportunity_quality,
               portfolio_alignment, related_projects, alert_status,
               email_date, created_at
        FROM job_scores
        WHERE match_score >= ?
        ORDER BY match_score DESC, created_at DESC
    """, (min_score,))


def all_jobs(limit=50):
    """All scored jobs."""
    return query_db("job_market", """
        SELECT job_title, company, location, work_type, experience_level,
               match_score, alert_status, email_date, created_at
        FROM job_scores
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))


def market_trends():
    """Weekly market trend summaries with formatted JSON fields."""
    rows = query_db("job_market", """
        SELECT week_start, total_jobs_scanned, new_jobs_this_week,
               avg_match_score, high_matches, medium_matches,
               top_skills, top_companies, top_locations,
               avg_compensation_min, avg_compensation_max
        FROM market_trends
        ORDER BY week_start DESC
        LIMIT 12
    """)
    for row in rows:
        row["top_skills"] = _format_json_list(row.get("top_skills"))
        row["top_companies"] = _format_json_list(row.get("top_companies"))
        row["top_locations"] = _format_json_list(row.get("top_locations"))
    return rows


def score_distribution():
    """Job count by score bracket."""
    return query_db("job_market", """
        SELECT
            CASE
                WHEN match_score >= 90 THEN '90-100'
                WHEN match_score >= 80 THEN '80-89'
                WHEN match_score >= 70 THEN '70-79'
                WHEN match_score >= 60 THEN '60-69'
                WHEN match_score >= 50 THEN '50-59'
                ELSE 'Below 50'
            END as bracket,
            COUNT(*) as count
        FROM job_scores
        GROUP BY bracket
        ORDER BY bracket DESC
    """)


def alert_status_distribution():
    """Count of jobs by alert status."""
    return query_db("job_market", """
        SELECT alert_status, COUNT(*) as count
        FROM job_scores
        GROUP BY alert_status
        ORDER BY count DESC
    """)


def total_jobs():
    return query_scalar("job_market", "SELECT COUNT(*) FROM job_scores")
