"""
Dra. Lina Web Application Factory.
"""
import os
import logging
from flask import Flask, render_template, jsonify
from .config import config
from .extensions import db, migrate, login_manager, csrf, jwt, cors, limiter


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

    # Configure logging
    log_level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config.get('CORS_ORIGINS', ['*']))
    limiter.init_app(app)

    # User loader (Flask-Login, kept for Jinja2 admin templates)
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # JWT blocklist check
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        from .routes.auth import BLOCKLIST
        return jwt_payload['jti'] in BLOCKLIST

    # Register legacy blueprints (Jinja2 templates)
    from .routes import public_bp, admin_bp, api_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Register new API blueprints
    from .routes.auth import auth_bp
    from .routes.api_v1 import api_v1_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_v1_bp)

    # Exempt API routes from CSRF (they use JWT)
    csrf.exempt(auth_bp)
    csrf.exempt(api_v1_bp)
    csrf.exempt(api_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('public/errors.html',
                               error_code=404,
                               error_title='Página no encontrada',
                               error_message='Lo sentimos, la página que estás buscando no existe.'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('public/errors.html',
                               error_code=500,
                               error_title='Error del servidor',
                               error_message='Ocurrió un error inesperado. Por favor intenta de nuevo más tarde.'), 500

    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({'error': 'Demasiadas solicitudes. Intenta de nuevo más tarde.'}), 429

    # Health check
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok'})

    # Import models for Alembic
    from . import models

    return app

