from flask import Blueprint, render_template

from queries.github_repos import all_saved_repos, saved_repo_count, repos_by_status

bp = Blueprint("github_repos", __name__)


@bp.route("/saved-repos")
def saved_repos_index():
    return render_template(
        "github_repos.html",
        active_page="saved_repos",
        repos=all_saved_repos(),
        repo_total=saved_repo_count(),
        status_counts=repos_by_status(),
    )
