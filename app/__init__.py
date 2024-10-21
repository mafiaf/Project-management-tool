from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()  # Create an instance of CSRFProtect

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate.init_app(app, db)

    # Initialize CSRF protection
    csrf.init_app(app)  # Bind the app to CSRF protection

    # Register routes
    from .routes import main
    app.register_blueprint(main)

    return app
