"""
Extensiones de Flask.
Instanciadas aquí sin vincular a la app, para evitar importaciones circulares.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)

login_manager.login_view = 'admin.admin_login'
