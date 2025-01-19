from flask import Flask
from config import Config

# Initialisation de l'application
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Importer les routes
    with app.app_context():
        from app.routes import bp as routes_bp
        app.register_blueprint(routes_bp)

    return app
