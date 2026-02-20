from flask import Blueprint, render_template

from queries.briefings import (
    all_briefings,
    briefing_detail,
    briefing_signals,
    signals_by_category,
)

bp = Blueprint("briefings", __name__)


@bp.route("/briefings")
def briefings_index():
    return render_template(
        "briefings.html",
        active_page="briefings",
        briefings=all_briefings(),
        signals=signals_by_category(),
    )


@bp.route("/briefings/<int:briefing_id>")
def briefing_show(briefing_id):
    briefing = briefing_detail(briefing_id)
    if not briefing:
        return render_template(
            "briefings.html",
            active_page="briefings",
            briefings=all_briefings(),
            signals=signals_by_category(),
        )
    return render_template(
        "briefing_detail.html",
        active_page="briefings",
        briefing=briefing,
        signals=briefing_signals(briefing_id),
    )
