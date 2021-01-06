class PyOSLC:

    def __init__(self, client):
        self._client = client
        self.headers = {
            'Accept': 'application/rdf+xml',
            'Content-Type': 'application/rdf+xml'
        }

    def get_catalog(self):
        return self._client.get(
            '/oslc/services/catalog',
            headers=self.headers
        )
