import pytest

from app import create_app
from app.config import Config


@pytest.fixture
def app():

    app = create_app(Config)

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class OSLCActions:
    """
    Action class for implementing the request of the list of requirements
    and the request for a specific requirement item
    """

    def __init__(self, client):
        self._client = client

    def list(self):
        """
        Method for listing the requirements/specifications
        taken from the synthetic data
        """

        headers = {
            'Content-Type': 'application/json-ld',
            'Accept': 'application/json-ld'
        }

        return self._client.get(
            'oslc/rm/requirement',
            headers=headers
        )

    def item(self, requirement_id):
        """
        Method for retrieving the information
        for a specific requirement/specification
        based on the id sent as parameter
        """

        headers = {
            'Content-Type': 'application/json-ld',
            'Accept': 'application/json-ld'
        }

        return self._client.get(
            'oslc/rm/requirement/' + requirement_id,
            headers=headers
        )


@pytest.fixture
def oslc(client):
    return OSLCActions(client)
