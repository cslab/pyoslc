import pytest

from webservice.api import create_app


@pytest.fixture
def app():

    app = create_app({
        'TESTING': True
    })

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class OSLCActions:

    def __init__(self, client):
        self._client = client

    def list(self):
        headers = {
            'Content-Type': 'application/json-ld',
            'Accept': 'application/json-ld'
        }

        return self._client.get(
            'api/1/catalog',
            headers=headers
        )


@pytest.fixture
def oslc(client):
    return OSLCActions(client)
