from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
from config import Config  # Import the Config class

db = SQLAlchemy()
migrate = Migrate()  # Create an instance of Migrate

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate.init_app(app, db)  # Bind app and db to Flask-Migrate

    # Register routes
    from .routes import main
    app.register_blueprint(main)

    return app
