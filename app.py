from flask import Flask

from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from routes.overview import bp as overview_bp
    from routes.cron_health import bp as cron_bp
    from routes.cost_tracking import bp as cost_bp
    from routes.content_pipeline import bp as content_bp
    from routes.projects import bp as projects_bp
    from routes.youtube import bp as youtube_bp
    from routes.jobs import bp as jobs_bp
    from routes.briefings import bp as briefings_bp
    from routes.knowledge_base import bp as kb_bp
    from routes.api import bp as api_bp
    from routes.twitter import bp as twitter_bp

    app.register_blueprint(overview_bp)
    app.register_blueprint(cron_bp)
    app.register_blueprint(cost_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(youtube_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(briefings_bp)
    app.register_blueprint(kb_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(twitter_bp)

    @app.context_processor
    def inject_sync_age():
        from db import get_data_freshness
        return {"sync_age": get_data_freshness()}

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
