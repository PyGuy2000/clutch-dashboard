import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "clutch-dashboard-dev-key")
    DB_BASE_PATH = os.environ.get("DB_BASE_PATH", "/app/data")

    DATABASES = {
        "cron_log": "cron_log.db",
        "usage_tracking": "usage_tracking.db",
        "content_ideas": "content_ideas.db",
        "knowledge_base": "knowledge_base.db",
        "job_market": "job_market.db",
        "youtube_channels": "youtube_channels.db",
        "briefings": "briefings.db",
        "projecthub": "projecthub.db",
        "twitter_trends": "twitter_trends.db",
    }

    @classmethod
    def db_path(cls, db_name):
        return os.path.join(cls.DB_BASE_PATH, cls.DATABASES[db_name])
