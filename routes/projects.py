from datetime import date

from flask import Blueprint, render_template

from queries.projects import (
    all_projects,
    project_detail,
    project_milestones,
    project_time_entries,
    summary_stats,
)

bp = Blueprint("projects", __name__)


@bp.route("/projects")
def projects_index():
    return render_template(
        "projects.html",
        active_page="projects",
        projects=all_projects(),
        stats=summary_stats(),
    )


@bp.route("/projects/<int:project_id>")
def project_show(project_id):
    project = project_detail(project_id)
    if not project:
        return render_template(
            "projects.html",
            active_page="projects",
            projects=all_projects(),
            stats=summary_stats(),
        )
    return render_template(
        "project_detail.html",
        active_page="projects",
        project=project,
        milestones=project_milestones(project_id),
        time_entries=project_time_entries(project_id),
        now_date=date.today().isoformat(),
    )
