from recap import create_app
from flask import g, session


def test_config():
    assert not create_app().testing
    app = create_app({'TESTING': True})
    assert app.testing
 

def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'

def test_config_from_env_file():
    app = create_app({'TESTING': True})
    assert app.config['API_KEY'] == 'abc123567'