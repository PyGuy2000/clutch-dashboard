from flask import Blueprint, render_template

from queries.overview import (
    cron_success_rate_24h,
    todays_cost,
    content_pipeline_counts,
    kb_stats,
    latest_briefing,
    high_match_jobs,
    youtube_trending,
    active_projects,
)

bp = Blueprint("overview", __name__)


@bp.route("/")
def index():
    return render_template(
        "overview.html",
        active_page="overview",
        cron=cron_success_rate_24h(),
        cost=todays_cost(),
        content=content_pipeline_counts(),
        kb=kb_stats(),
        briefing=latest_briefing(),
        jobs=high_match_jobs(),
        youtube=youtube_trending(),
        projects=active_projects(),
    )
