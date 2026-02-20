from flask import Blueprint, render_template

from queries.cron_health import (
    all_jobs_summary,
    stale_jobs,
    job_runs,
    total_jobs_count,
)

bp = Blueprint("cron_health", __name__)


@bp.route("/cron")
def cron_index():
    return render_template(
        "cron_health.html",
        active_page="cron",
        jobs=all_jobs_summary(),
        stale=stale_jobs(),
        total_jobs=total_jobs_count(),
    )


@bp.route("/cron/<job_name>")
def cron_detail(job_name):
    return render_template(
        "cron_job_detail.html",
        active_page="cron",
        job_name=job_name,
        runs=job_runs(job_name),
    )
