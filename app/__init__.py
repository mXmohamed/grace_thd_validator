from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # S'assurer que le dossier d'upload existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    
    # Enregistrer les routes
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app