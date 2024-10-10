from flask import Flask  # Make sure this is included
from flask_sqlalchemy import SQLAlchemy
from config import Config  # Import the Config class

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    try:
        # Configuration
        app.config.from_object(Config)
    except Exception as e:
        print(f"Error loading configuration: {e}")

    # Initialize database
    db.init_app(app)

    # Register routes
    from .routes import main
    app.register_blueprint(main)

    return app