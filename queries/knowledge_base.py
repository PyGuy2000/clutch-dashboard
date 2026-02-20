from db import query_db, query_scalar


def sources_by_type():
    """Source count grouped by type."""
    return query_db("knowledge_base", """
        SELECT source_type, COUNT(*) as count
        FROM sources
        GROUP BY source_type
        ORDER BY count DESC
    """)


def recent_sources(limit=30):
    """Recently added sources."""
    return query_db("knowledge_base", """
        SELECT id, title, source_type, url, summary,
               created_at
        FROM sources
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))


def source_titles_by_type(source_type, limit=50):
    """All sources of a given type."""
    return query_db("knowledge_base", """
        SELECT id, title, url, summary, created_at
        FROM sources
        WHERE source_type = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (source_type, limit))


def all_sources_summary():
    """All sources with title and type for browsing."""
    return query_db("knowledge_base", """
        SELECT id, title, source_type, url,
               SUBSTR(summary, 1, 200) as summary_short,
               created_at
        FROM sources
        ORDER BY created_at DESC
    """)


def total_stats():
    sources = query_scalar("knowledge_base", "SELECT COUNT(*) FROM sources")
    chunks = query_scalar("knowledge_base", "SELECT COUNT(*) FROM chunks")
    return {"sources": sources, "chunks": chunks}


def acquisition_recent(limit=10):
    """Recent KB acquisitions."""
    return query_db("knowledge_base", """
        SELECT a.scan_source, a.discovery_date, s.title, s.source_type
        FROM acquisition_metadata a
        JOIN sources s ON a.source_id = s.id
        ORDER BY a.created_at DESC
        LIMIT ?
    """, (limit,))
