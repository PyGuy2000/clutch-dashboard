from flask import Blueprint, render_template

from queries.github_activity import (
    activity_stats,
    commits_per_repo_week,
    daily_commit_counts,
    open_pull_requests,
    recent_commits,
    recent_merged_prs,
    repo_summary,
)

bp = Blueprint("github_activity", __name__)


@bp.route("/github")
def github_index():
    return render_template(
        "github_activity.html",
        active_page="github",
        stats=activity_stats(),
        recent=recent_commits(50),
        open_prs=open_pull_requests(),
        merged_prs=recent_merged_prs(20),
        repos=repo_summary(),
        commits_by_repo=commits_per_repo_week(),
        daily_commits=daily_commit_counts(30),
    )
