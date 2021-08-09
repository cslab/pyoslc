from pyoslc_server.api import OSLCAPI


class OSLCEnabled:

    def __init__(self):
        self.api = OSLCAPI('/oslc')

    def __call__(self, environ, start_response):
        """
        Callable function required
        """

        if self.api.wsgi_check(environ):
            return self.api(environ, start_response)

        start_response("200 OK", [('Content-type', 'text/plain')])
        return [b'Hello World, This could be a CE Application !']
