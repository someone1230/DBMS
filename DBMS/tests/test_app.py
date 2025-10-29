def test_index_page(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data

def test_login_page(test_client):
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data

def test_register_page(test_client):
    response = test_client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_login_with_valid_credentials(test_client, init_database):
    response = test_client.post('/login', data=dict(
        username='testuser',
        password='testpass',
        remember_me=False
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome' in response.data

def test_login_with_invalid_credentials(test_client):
    response = test_client.post('/login', data=dict(
        username='wronguser',
        password='wrongpass'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data
