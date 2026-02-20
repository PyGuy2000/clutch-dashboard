from flask import Blueprint, render_template

from queries.content_pipeline import (
    ideas_by_status,
    post_type_distribution,
    dedup_stats,
    recent_activity,
    status_counts,
)

bp = Blueprint("content_pipeline", __name__)


@bp.route("/content")
def content_index():
    return render_template(
        "content_pipeline.html",
        active_page="content",
        ideas=ideas_by_status(),
        types=post_type_distribution(),
        dedup=dedup_stats(),
        recent=recent_activity(),
        counts=status_counts(),
    )
