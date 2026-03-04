"""
Integration tests for public and admin routes.
"""


def test_index_returns_200(client):
    response = client.get('/')
    assert response.status_code == 200


def test_blog_returns_200(client):
    response = client.get('/blog')
    assert response.status_code == 200


def test_reservar_get_returns_200(client):
    response = client.get('/reservar')
    assert response.status_code == 200


def test_terminos_returns_200(client):
    response = client.get('/terminos')
    assert response.status_code == 200


def test_404_returns_custom_page(client):
    response = client.get('/pagina-que-no-existe-abc123')
    assert response.status_code == 404
    assert 'Página no encontrada' in response.data.decode('utf-8')


def test_admin_login_get_returns_200(client):
    response = client.get('/admin/login')
    assert response.status_code == 200


def test_admin_dashboard_requires_login(client):
    response = client.get('/admin/', follow_redirects=False)
    assert response.status_code == 302
    assert '/admin/login' in response.headers.get('Location', '')
