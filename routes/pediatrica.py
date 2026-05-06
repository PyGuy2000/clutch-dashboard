from flask import Blueprint, render_template, jsonify

from queries.pediatrica import get_pediatrica_health

bp = Blueprint("pediatrica", __name__)


@bp.route("/pediatrica")
def pediatrica_index():
    health = get_pediatrica_health()
    return render_template(
        "pediatrica.html",
        active_page="pediatrica",
        health=health,
    )


@bp.route("/api/pediatrica/health")
def api_pediatrica_health():
    """JSON endpoint for nightly briefing integration."""
    return jsonify(get_pediatrica_health())
