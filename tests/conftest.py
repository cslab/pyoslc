import pytest

# from app import create_app
# from app.config import Config
from tests.functional.oslc import PyOSLC

from apposlc import create_oslc_app


# @pytest.fixture(scope='session')
# def client():
#     """
#     Getting the test_client instance for the Flask application
#     for executing and validating the tests
#
#     :param app: Flask application
#     :return: client: Client with test configuration
#     """
#     # Create a test client using the Flask application configured for testing
#     app = create_app(Config)
#     app.testing = True
#     with app.test_client() as client:
#         # Establish an application context
#         with app.app_context():
#             yield client  # this is where the testing happens!


@pytest.fixture(scope='session')
def client_oslc():
    oslc_app = create_oslc_app()
    oslc_app.app.testing = True
    with oslc_app.app.test_client() as client:
        with oslc_app.app.app_context():
            yield client  # this is where the testing happens!


@pytest.fixture
def pyoslc(client):
    return PyOSLC(client)


@pytest.fixture
def pyoslc_enabled(client_oslc):
    return PyOSLC(client_oslc)
