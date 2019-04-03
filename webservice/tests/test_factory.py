from webservice.api import create_app


def test_config():
    """
    Testing the factory approach of the application
    passing different values for the configuration
    """
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing
    assert create_app({'TESTING': True}).config['LOG_TO_STDOUT'] is None


def test_index(client):
    """
    Testing the information of the index page
    """
    response = client.get('/')
    assert b'An OSLC adapter implemented on Python.' in response.data
