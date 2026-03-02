from flask import Blueprint, render_template

from queries.jobs import (
    high_match_jobs,
    all_jobs,
    market_trends,
    score_distribution,
    alert_status_distribution,
    total_jobs,
)

bp = Blueprint("jobs", __name__)


@bp.route("/jobs")
def jobs_index():
    statuses = alert_status_distribution()
    status_map = {r["alert_status"]: r["count"] for r in statuses}
    return render_template(
        "jobs.html",
        active_page="jobs",
        high_matches=high_match_jobs(),
        all_jobs=all_jobs(),
        trends=market_trends(),
        distribution=score_distribution(),
        status_map=status_map,
        total=total_jobs(),
    )
