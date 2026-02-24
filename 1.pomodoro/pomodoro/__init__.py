from flask import Flask

from .routes import main_bp


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)

    if config:
        app.config.update(config)

    app.register_blueprint(main_bp)
    return app
