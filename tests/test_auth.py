"""
Tests for JWT authentication: login, refresh, logout, me.
"""


def test_login_success(client, db_session):
    from app.models import User
    from werkzeug.security import generate_password_hash

    user = User(
        username='admin_test',
        password_hash=generate_password_hash('secretpass'),
        role='admin'
    )
    db_session.add(user)
    db_session.commit()

    response = client.post('/api/v1/auth/login', json={
        'username': 'admin_test',
        'password': 'secretpass'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['username'] == 'admin_test'


def test_login_wrong_password(client):
    response = client.post('/api/v1/auth/login', json={
        'username': 'noexist',
        'password': 'wrong'
    })
    assert response.status_code == 401


def test_login_missing_fields(client):
    response = client.post('/api/v1/auth/login', json={})
    assert response.status_code == 400


def test_me_without_token(client):
    response = client.get('/api/v1/auth/me')
    assert response.status_code == 401


def test_me_with_token(client, db_session):
    from app.models import User
    from werkzeug.security import generate_password_hash

    user = User(
        username='admin_me',
        password_hash=generate_password_hash('pass123'),
        role='admin'
    )
    db_session.add(user)
    db_session.commit()

    login = client.post('/api/v1/auth/login', json={
        'username': 'admin_me',
        'password': 'pass123'
    })
    token = login.get_json()['access_token']

    response = client.get('/api/v1/auth/me', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert response.get_json()['username'] == 'admin_me'


def test_refresh_token(client, db_session):
    from app.models import User
    from werkzeug.security import generate_password_hash

    user = User(
        username='admin_refresh',
        password_hash=generate_password_hash('pass'),
        role='admin'
    )
    db_session.add(user)
    db_session.commit()

    login = client.post('/api/v1/auth/login', json={
        'username': 'admin_refresh',
        'password': 'pass'
    })
    refresh_token = login.get_json()['refresh_token']

    response = client.post('/api/v1/auth/refresh', headers={
        'Authorization': f'Bearer {refresh_token}'
    })
    assert response.status_code == 200
    assert 'access_token' in response.get_json()


def test_logout_revokes_token(client, db_session):
    from app.models import User
    from werkzeug.security import generate_password_hash

    user = User(
        username='admin_logout',
        password_hash=generate_password_hash('pass'),
        role='admin'
    )
    db_session.add(user)
    db_session.commit()

    login = client.post('/api/v1/auth/login', json={
        'username': 'admin_logout',
        'password': 'pass'
    })
    token = login.get_json()['access_token']

    # Logout
    response = client.delete('/api/v1/auth/logout', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200

    # Token should be revoked
    response = client.get('/api/v1/auth/me', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 401
