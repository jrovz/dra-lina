"""
Pytest configuration and fixtures for dra-lina-web.
"""
import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db_session(app):
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()

        yield _db.session

        _db.session.remove()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()
