from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enregistrer les blueprints
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
