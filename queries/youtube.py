from db import query_db, query_scalar


def trending_phrases():
    """All phrases ordered by occurrence count."""
    return query_db("youtube_channels", """
        SELECT phrase, category, occurrence_count, trending,
               first_seen_channel, first_seen_date, created_at
        FROM phrases
        ORDER BY occurrence_count DESC, created_at DESC
    """)


def phrases_by_category():
    """Phrase counts grouped by category."""
    return query_db("youtube_channels", """
        SELECT category, COUNT(*) as count,
               SUM(CASE WHEN trending = 1 THEN 1 ELSE 0 END) as trending_count
        FROM phrases
        GROUP BY category
        ORDER BY count DESC
    """)


def channels():
    """All tracked channels."""
    return query_db("youtube_channels", """
        SELECT name, category, domain_tags, active, last_scan_date,
               total_videos_tracked
        FROM channels
        ORDER BY name
    """)


def recent_videos(limit=20):
    """Recently discovered videos."""
    return query_db("youtube_channels", """
        SELECT title, channel_name, upload_date, view_count,
               content_flag, domain_tags, video_url
        FROM videos
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))


def video_count():
    return query_scalar("youtube_channels", "SELECT COUNT(*) FROM videos")


def channel_count():
    return query_scalar("youtube_channels", "SELECT COUNT(*) FROM channels")
