"""
Tests for API v1 public and admin endpoints.
"""
import uuid


def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'


def test_list_services(client):
    response = client.get('/api/v1/services')
    assert response.status_code == 200
    assert 'data' in response.get_json()


def test_list_doctors(client):
    response = client.get('/api/v1/doctors')
    assert response.status_code == 200
    assert 'data' in response.get_json()


def test_list_posts(client):
    response = client.get('/api/v1/blog/posts')
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert 'pagination' in data


def test_get_post_not_found(client):
    response = client.get('/api/v1/blog/posts/nonexistent-slug')
    assert response.status_code == 404


def test_admin_posts_requires_jwt(client):
    response = client.get('/api/v1/admin/posts')
    assert response.status_code == 401


def test_admin_dashboard_requires_jwt(client):
    response = client.get('/api/v1/admin/dashboard/stats')
    assert response.status_code == 401


def _get_jwt_token(client, db_session):
    from app.models import User
    from werkzeug.security import generate_password_hash

    uname = f'api_admin_{uuid.uuid4().hex[:8]}'
    user = User(username=uname, password_hash=generate_password_hash('pass'), role='admin')
    db_session.add(user)
    db_session.commit()
    login = client.post('/api/v1/auth/login', json={'username': uname, 'password': 'pass'})
    return login.get_json()['access_token']


def test_admin_posts_with_jwt(client, db_session):
    token = _get_jwt_token(client, db_session)
    response = client.get('/api/v1/admin/posts', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert 'data' in response.get_json()
    assert 'pagination' in response.get_json()


def test_admin_create_post(client, db_session):
    token = _get_jwt_token(client, db_session)
    response = client.post('/api/v1/admin/posts',
        json={'title': 'Test Post', 'content': 'Hello world', 'slug': 'test-post'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    assert response.get_json()['data']['title'] == 'Test Post'


def test_admin_dashboard_stats(client, db_session):
    token = _get_jwt_token(client, db_session)
    response = client.get('/api/v1/admin/dashboard/stats', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    data = response.get_json()['data']
    assert 'appointments_today' in data
    assert 'posts_published' in data


def test_create_appointment_validation(client):
    response = client.post('/api/v1/appointments', json={})
    assert response.status_code == 400
