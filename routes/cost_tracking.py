from flask import Blueprint, render_template

from queries.cost_tracking import (
    active_alerts,
    monthly_projection,
    total_spend_month,
)

bp = Blueprint("cost_tracking", __name__)


@bp.route("/costs")
def costs_index():
    return render_template(
        "cost_tracking.html",
        active_page="costs",
        alerts=active_alerts(),
        projection=monthly_projection(),
        month_total=round(total_spend_month(), 4),
    )
