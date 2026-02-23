from db import query_scalar, query_db


def recipe_count():
    return query_scalar("meal_planning", "SELECT COUNT(*) FROM recipes")


def active_plan():
    return query_db("meal_planning", """
        SELECT id, week_start, status FROM meal_plans
        WHERE status IN ('active', 'draft')
        ORDER BY CASE status WHEN 'active' THEN 1 WHEN 'draft' THEN 2 END
        LIMIT 1
    """, one=True)


def this_week_meals():
    plan = active_plan()
    if not plan or not plan.get("id"):
        return []
    return query_db("meal_planning", """
        SELECT pm.day_of_week,
               CASE pm.day_of_week
                   WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday'
                   WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday'
                   WHEN 5 THEN 'Friday' WHEN 6 THEN 'Saturday'
                   WHEN 7 THEN 'Sunday'
               END AS day_name,
               pm.meal_type,
               COALESCE(r.name, pm.freetext_meal) AS meal_name,
               pm.notes
        FROM planned_meals pm
        LEFT JOIN recipes r ON pm.recipe_id = r.id
        WHERE pm.plan_id = ?
        ORDER BY pm.day_of_week,
            CASE pm.meal_type
                WHEN 'breakfast' THEN 1 WHEN 'lunch' THEN 2
                WHEN 'dinner' THEN 3 WHEN 'snack' THEN 4
            END
    """, (plan["id"],))


def todays_dinner():
    plan = active_plan()
    if not plan or not plan.get("id"):
        return None
    row = query_db("meal_planning", """
        SELECT COALESCE(r.name, pm.freetext_meal) AS meal_name,
               r.prep_time_min, pm.notes
        FROM planned_meals pm
        LEFT JOIN recipes r ON pm.recipe_id = r.id
        WHERE pm.plan_id = ?
          AND pm.meal_type = 'dinner'
          AND pm.day_of_week = CASE CAST(strftime('%w', 'now') AS INTEGER)
              WHEN 0 THEN 7 ELSE CAST(strftime('%w', 'now') AS INTEGER) END
        LIMIT 1
    """, (plan["id"],), one=True)
    return row if row else None


def preference_count():
    return query_scalar("meal_planning", "SELECT COUNT(*) FROM preferences WHERE active = 1")


def top_recipes(limit=10):
    return query_db("meal_planning", """
        SELECT name, meal_type, rating, times_made, prep_time_min
        FROM recipes
        ORDER BY COALESCE(rating, 0) DESC, times_made DESC
        LIMIT ?
    """, (limit,))
