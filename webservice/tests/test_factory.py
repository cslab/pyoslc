from webservice.api import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing
    assert create_app({'TESTING': True}).config['LOG_TO_STDOUT'] is None


def test_index(client):
    response = client.get('/')
    assert b'Python OSLC Adapter' in response.data
