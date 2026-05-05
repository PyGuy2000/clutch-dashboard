from flask import Blueprint, render_template

from queries.repos import all_repos, repo_count, milestone_count

bp = Blueprint("repos", __name__)


@bp.route("/repos")
def repos_index():
    return render_template(
        "repos.html",
        active_page="repos",
        repos=all_repos(),
        repo_total=repo_count(),
        milestone_total=milestone_count(),
    )
