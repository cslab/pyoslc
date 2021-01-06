import pytest

from app import create_app
from app.config import Config
from tests.functional.oslc import PyOSLC


@pytest.fixture(scope='session')
def app():
    """
    Initializing the Flask application for the Minerva OSLC API
    by passing the Config class as the configuration

    :return: app: Flask application
    """
    app = create_app('testing')
    app.testing = True
    yield app


@pytest.fixture(scope='session')
def client():
    """
    Getting the test_client instance for the Flask application
    for executing and validating the tests

    :param app: Flask application
    :return: client: Client with test configuration
    """
    # Create a test client using the Flask application configured for testing
    app = create_app(Config)
    app.testing = True
    with app.test_client() as client:
        # Establish an application context
        with app.app_context():
            yield client  # this is where the testing happens!


@pytest.fixture
def pyoslc(client):
    return PyOSLC(client)
