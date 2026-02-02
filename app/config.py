"""
Configuración de la aplicación Flask.
Clases para diferentes entornos: Development, Production, Testing.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key_for_dra_lina')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///dra_lina.db')


class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class TestingConfig(Config):
    """Configuración para tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
