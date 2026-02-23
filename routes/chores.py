from flask import Blueprint, render_template

from queries.chores import (
    kid_count,
    chore_count,
    todays_assignments,
    weekly_completion_rates,
    pending_count_today,
    recent_completions,
)

bp = Blueprint("chores", __name__)


@bp.route("/chores")
def chores_index():
    return render_template(
        "chores.html",
        active_page="chores",
        kids=kid_count(),
        chores=chore_count(),
        pending=pending_count_today(),
        assignments=todays_assignments(),
        weekly=weekly_completion_rates(),
        completions=recent_completions(),
    )
