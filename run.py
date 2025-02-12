import sys
import os

# Ensure your virtual environment or PYTHONPATH is correctly configured

from app import create_app

app = create_app()

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)