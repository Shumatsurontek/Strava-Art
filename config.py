import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuration générale
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-secret-key'

    # Configuration Flask
    DEBUG = True


    GPX_FILES_DIR = os.getenv("GPX_FILES_DIR", "gpx_files")
    MAP_FILES_DIR = os.getenv("MAP_FILES_DIR", "map_files")
    @staticmethod
    def init_app(app):
        # Créez les dossiers s'ils n'existent pas
        os.makedirs(Config.GPX_FILES_DIR, exist_ok=True)
        os.makedirs(Config.MAP_FILES_DIR, exist_ok=True)

