from db import query_db, query_scalar


def high_match_jobs(min_score=70):
    """Jobs above score threshold."""
    return query_db("job_market", """
        SELECT job_title, company, location, work_type, experience_level,
               match_score, skill_match, experience_match, opportunity_quality,
               portfolio_alignment, related_projects, email_date, created_at
        FROM job_scores
        WHERE match_score >= ?
        ORDER BY match_score DESC, created_at DESC
    """, (min_score,))


def all_jobs(limit=50):
    """All scored jobs."""
    return query_db("job_market", """
        SELECT job_title, company, location, work_type, experience_level,
               match_score, email_date, created_at
        FROM job_scores
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))


def market_trends():
    """Weekly market trend summaries."""
    return query_db("job_market", """
        SELECT week_start, total_jobs_scanned, new_jobs_this_week,
               avg_match_score, high_matches, medium_matches,
               top_skills, top_companies, top_locations
        FROM market_trends
        ORDER BY week_start DESC
        LIMIT 12
    """)


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


def total_jobs():
    return query_scalar("job_market", "SELECT COUNT(*) FROM job_scores")
