from flask import Blueprint, jsonify

from queries.cron_health import job_duration_history
from queries.cost_tracking import daily_spend, model_breakdown, skill_breakdown
from queries.content_pipeline import publishing_pace_weekly

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/cron/<job_name>/duration")
def cron_duration(job_name):
    data = job_duration_history(job_name)
    return jsonify({
        "labels": [r["started_at"] for r in data],
        "values": [r["duration_seconds"] for r in data],
    })


@bp.route("/costs/daily")
def costs_daily():
    data = daily_spend()
    return jsonify({
        "labels": [r["day"] for r in data],
        "values": [round(r["total_cost"], 4) for r in data],
    })


@bp.route("/costs/models")
def costs_models():
    data = model_breakdown()
    return jsonify({
        "labels": [r["model"] for r in data],
        "values": [round(r["total_cost"], 4) for r in data],
        "counts": [r["call_count"] for r in data],
    })


@bp.route("/costs/skills")
def costs_skills():
    data = skill_breakdown()
    return jsonify({
        "labels": [r["skill"] for r in data],
        "values": [round(r["total_cost"], 4) for r in data],
        "counts": [r["call_count"] for r in data],
    })


@bp.route("/content/pace")
def content_pace():
    data = publishing_pace_weekly()
    return jsonify({
        "labels": [r["week"] for r in data],
        "values": [r["count"] for r in data],
    })
