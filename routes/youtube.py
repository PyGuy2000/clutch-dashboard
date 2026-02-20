from flask import Blueprint, render_template

from queries.youtube import (
    trending_phrases,
    phrases_by_category,
    channels,
    recent_videos,
    video_count,
    channel_count,
)

bp = Blueprint("youtube", __name__)


@bp.route("/youtube")
def youtube_index():
    return render_template(
        "youtube.html",
        active_page="youtube",
        phrases=trending_phrases(),
        categories=phrases_by_category(),
        channels=channels(),
        videos=recent_videos(),
        video_total=video_count(),
        channel_total=channel_count(),
    )
