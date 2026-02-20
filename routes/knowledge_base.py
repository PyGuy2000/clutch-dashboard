from flask import Blueprint, render_template

from queries.knowledge_base import (
    sources_by_type,
    recent_sources,
    all_sources_summary,
    total_stats,
    acquisition_recent,
)

bp = Blueprint("knowledge_base", __name__)


@bp.route("/kb")
def kb_index():
    return render_template(
        "knowledge_base.html",
        active_page="kb",
        by_type=sources_by_type(),
        sources=all_sources_summary(),
        stats=total_stats(),
        acquisitions=acquisition_recent(),
    )
