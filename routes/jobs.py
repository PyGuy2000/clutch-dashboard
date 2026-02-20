from flask import Blueprint, render_template

from queries.jobs import (
    high_match_jobs,
    all_jobs,
    market_trends,
    score_distribution,
    total_jobs,
)

bp = Blueprint("jobs", __name__)


@bp.route("/jobs")
def jobs_index():
    return render_template(
        "jobs.html",
        active_page="jobs",
        high_matches=high_match_jobs(),
        all_jobs=all_jobs(),
        trends=market_trends(),
        distribution=score_distribution(),
        total=total_jobs(),
    )
