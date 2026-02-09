"""
Dra. Lina Web Application Factory.
"""
import os
from flask import Flask
from .config import config
from .extensions import db, migrate, login_manager, csrf


def create_app(config_name=None):
    """
    Application Factory.
    
    Args:
        config_name: Nombre de la configuración ('development', 'production', 'testing').
                     Si no se especifica, se usa FLASK_ENV o 'development'.
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    
    app.config.from_object(config[config_name])

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # Registrar Blueprints
    from .routes import public_bp, admin_bp, api_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Importar modelos para que Alembic los detecte
    from . import models

    return app
