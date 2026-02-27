from db import query_db, query_scalar


def contact_count():
    return query_scalar("crm", "SELECT COUNT(*) FROM contacts")


def company_count():
    return query_scalar("crm", "SELECT COUNT(*) FROM companies")


def deal_count():
    return query_scalar("crm", "SELECT COUNT(*) FROM deals")


def high_value_count():
    return query_scalar("crm", """
        SELECT COUNT(*) FROM relationship_scores WHERE total_score >= 70
    """)


def stale_count():
    return query_scalar("crm", """
        SELECT COUNT(*) FROM relationship_scores
        WHERE (total_score >= 70 AND days_since_contact >= 14)
           OR (total_score >= 50 AND days_since_contact >= 30)
    """)


def pipeline_value():
    return query_scalar("crm", """
        SELECT COALESCE(SUM(amount), 0) FROM deals
        WHERE deal_stage NOT IN ('closedwon', 'closedlost')
    """, default=0.0)


def pending_drafts_count():
    return query_scalar("crm", """
        SELECT COUNT(*) FROM follow_up_drafts WHERE draft_status = 'pending'
    """)


def contacts_with_scores():
    return query_db("crm", """
        SELECT c.firstname, c.lastname, c.company_name, c.job_title, c.email,
               COALESCE(rs.total_score, 0) AS total_score,
               COALESCE(rs.engagement, 0) AS engagement,
               COALESCE(rs.strategic_fit, 0) AS strategic_fit,
               COALESCE(rs.opportunity_potential, 0) AS opportunity_potential,
               COALESCE(rs.network_value, 0) AS network_value,
               rs.days_since_contact,
               rs.nudge_status
        FROM contacts c
        LEFT JOIN relationship_scores rs ON c.id = rs.contact_id
        ORDER BY COALESCE(rs.total_score, 0) DESC
    """)


def companies_list():
    return query_db("crm", """
        SELECT co.name, co.industry, co.num_employees, co.domain,
               co.research_summary, co.research_date,
               (SELECT COUNT(*) FROM contacts c WHERE c.company_name = co.name) AS contact_count
        FROM companies co
        ORDER BY co.name
    """)


def deals_list():
    return query_db("crm", """
        SELECT d.deal_name, d.deal_stage, d.amount, d.close_date, d.deal_type,
               c.firstname || ' ' || c.lastname AS contact_name,
               co.name AS company_name
        FROM deals d
        LEFT JOIN contacts c ON d.contact_id = c.id
        LEFT JOIN companies co ON d.company_id = co.id
        ORDER BY d.deal_stage, d.close_date
    """)


def pending_drafts():
    return query_db("crm", """
        SELECT fd.draft_subject, fd.draft_status, fd.context_summary, fd.created_at,
               c.firstname || ' ' || c.lastname AS contact_name
        FROM follow_up_drafts fd
        JOIN contacts c ON fd.contact_id = c.id
        WHERE fd.draft_status = 'pending'
        ORDER BY fd.created_at DESC
    """)


def last_sync():
    return query_db("crm", """
        SELECT sync_type, records_fetched, records_created, records_updated,
               status, error_message, started_at, completed_at
        FROM sync_log
        ORDER BY started_at DESC
        LIMIT 1
    """, one=True)


def score_distribution():
    return query_db("crm", """
        SELECT
            CASE
                WHEN rs.total_score >= 70 THEN '70+'
                WHEN rs.total_score >= 50 THEN '50-69'
                WHEN rs.total_score >= 25 THEN '25-49'
                ELSE '<25'
            END AS bracket,
            COUNT(*) AS count
        FROM relationship_scores rs
        GROUP BY bracket
        ORDER BY rs.total_score DESC
    """)


def crm_summary():
    """Summary stats for the overview page."""
    return {
        "contacts": contact_count(),
        "high_value": high_value_count(),
        "stale": stale_count(),
        "pipeline_value": pipeline_value(),
    }
