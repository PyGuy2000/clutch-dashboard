from db import query_db


def all_briefings():
    """All briefings with metadata."""
    return query_db("briefings", """
        SELECT id, date, momentum_weekly, momentum_monthly, theme,
               content, estimated_cost, created_at
        FROM briefings
        WHERE theme IS NOT NULL
        ORDER BY created_at DESC
    """)


def briefing_detail(briefing_id):
    """Single briefing with full content."""
    return query_db("briefings", """
        SELECT * FROM briefings WHERE id = ?
    """, (briefing_id,), one=True)


def briefing_signals(briefing_id):
    """Signals for a specific briefing."""
    return query_db("briefings", """
        SELECT source, signal_name, value, direction, category
        FROM signals
        WHERE briefing_id = ?
        ORDER BY category, source
    """, (briefing_id,))


def latest_signals():
    """Signals from the most recent briefing with data."""
    return query_db("briefings", """
        SELECT s.source, s.signal_name, s.value, s.direction, s.category
        FROM signals s
        JOIN briefings b ON s.briefing_id = b.id
        WHERE b.theme IS NOT NULL
        ORDER BY b.created_at DESC, s.category, s.source
    """)


def signals_by_category():
    """Latest signals grouped by category."""
    signals = latest_signals()
    grouped = {}
    for s in signals:
        cat = s["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(s)
    return grouped
