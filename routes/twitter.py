from flask import Blueprint, render_template

from queries.twitter import (
    account_count,
    tweet_count,
    tweets_today,
    trending_theme_count,
    cross_source_count,
    themes_by_status,
    trending_themes,
    flagged_tweets,
    cross_source_themes,
    accounts,
    accounts_by_category,
    theme_velocity_history,
)

bp = Blueprint("twitter", __name__)


@bp.route("/twitter")
def twitter_index():
    return render_template(
        "twitter.html",
        active_page="twitter",
        account_total=account_count(),
        tweet_total=tweet_count(),
        tweets_today_count=tweets_today(),
        trending_count=trending_theme_count(),
        cross_source_total=cross_source_count(),
        status_counts=themes_by_status(),
        themes=trending_themes(),
        flagged=flagged_tweets(),
        convergences=cross_source_themes(),
        accts=accounts(),
        categories=accounts_by_category(),
        velocity_history=theme_velocity_history(),
    )
