from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.routes import dashboard, meals

    app.register_blueprint(dashboard.bp)
    app.register_blueprint(meals.bp)

    return app