from flask import Blueprint, render_template

from queries.meals import (
    recipe_count,
    active_plan,
    this_week_meals,
    todays_dinner,
    preference_count,
    top_recipes,
)

bp = Blueprint("meals", __name__)


@bp.route("/meals")
def meals_index():
    return render_template(
        "meals.html",
        active_page="meals",
        recipes=recipe_count(),
        plan=active_plan(),
        meals=this_week_meals(),
        dinner=todays_dinner(),
        preferences=preference_count(),
        top=top_recipes(),
    )
