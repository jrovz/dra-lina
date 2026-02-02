"""
Extensiones de Flask.
Instanciadas aquí sin vincular a la app, para evitar importaciones circulares.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'admin.admin_login'
