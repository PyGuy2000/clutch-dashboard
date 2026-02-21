from db import query_db, query_scalar


def account_count():
    return query_scalar("twitter_trends", "SELECT COUNT(*) FROM accounts WHERE active = 1")


def tweet_count():
    return query_scalar("twitter_trends", "SELECT COUNT(*) FROM tweets")


def tweets_today():
    return query_scalar("twitter_trends", """
        SELECT COUNT(*) FROM tweets WHERE date(created_at) >= date('now')
    """)


def trending_theme_count():
    return query_scalar("twitter_trends", """
        SELECT COUNT(*) FROM themes WHERE status = 'trending'
    """)


def cross_source_count():
    return query_scalar("twitter_trends", """
        SELECT COUNT(*) FROM cross_source_themes WHERE correlation_score >= 0.3
    """)


def themes_by_status():
    """Theme counts grouped by status."""
    return query_db("twitter_trends", """
        SELECT status, COUNT(*) as count
        FROM themes
        GROUP BY status
        ORDER BY CASE status
            WHEN 'trending' THEN 1
            WHEN 'active' THEN 2
            WHEN 'emerging' THEN 3
            WHEN 'declining' THEN 4
            WHEN 'stale' THEN 5
        END
    """)


def trending_themes():
    """All themes ordered by velocity."""
    return query_db("twitter_trends", """
        SELECT name, description, mention_count, unique_accounts,
               velocity, acceleration, status, first_seen_date, updated_at
        FROM themes
        ORDER BY CASE status
            WHEN 'trending' THEN 1
            WHEN 'active' THEN 2
            WHEN 'emerging' THEN 3
            WHEN 'declining' THEN 4
            WHEN 'stale' THEN 5
        END, velocity DESC
    """)


def flagged_tweets(limit=30):
    """Content-flagged tweets with account info."""
    return query_db("twitter_trends", """
        SELECT t.text, t.content_angle, t.likes, t.retweets,
               t.domain_tags, t.posted_at, t.tweet_url, t.created_at,
               a.handle, a.category
        FROM tweets t
        JOIN accounts a ON t.account_id = a.id
        WHERE t.content_flag = 1
        ORDER BY t.created_at DESC
        LIMIT ?
    """, (limit,))


def cross_source_themes():
    """Cross-source convergences."""
    return query_db("twitter_trends", """
        SELECT theme_name, twitter_count, youtube_count, kb_count,
               source_types, correlation_score, first_detected, last_updated
        FROM cross_source_themes
        ORDER BY correlation_score DESC
    """)


def accounts():
    """All tracked accounts."""
    return query_db("twitter_trends", """
        SELECT handle, display_name, category, domain_tags, active,
               last_scan_date, total_tweets_tracked
        FROM accounts
        ORDER BY category, handle
    """)


def accounts_by_category():
    """Account counts per category."""
    return query_db("twitter_trends", """
        SELECT category, COUNT(*) as count,
               SUM(total_tweets_tracked) as total_tweets
        FROM accounts
        WHERE active = 1
        GROUP BY category
        ORDER BY count DESC
    """)


def theme_velocity_history(limit=14):
    """Daily velocity data for top themes (for Chart.js)."""
    return query_db("twitter_trends", """
        SELECT th.date, t.name, th.velocity, th.mention_count
        FROM theme_history th
        JOIN themes t ON th.theme_id = t.id
        WHERE t.status IN ('trending', 'active')
        AND th.date >= date('now', ? || ' days')
        ORDER BY th.date, t.name
    """, (str(-limit),))
