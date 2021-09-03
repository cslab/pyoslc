from pyoslc_server import OSLCAPP

from apposlc.adapter import RequirementAdapter, TestCaseAdapter


class OSLCEnabled:

    def __init__(self):
        self.app = OSLCAPP(prefix='/oslc')
        self.app.api.add_adapter(
            identifier='adapter',
            title='Requirement Adapter',
            description='Requirement Adapter for OSLC',
            klass=RequirementAdapter,
        )

        self.app.api.add_adapter('tests', 'test cases', 'test cases', TestCaseAdapter)

    def __call__(self, environ, start_response):
        """
        Callable function required
        """

        if self.app.wsgi_check(environ):
            return self.app(environ, start_response)

        start_response("200 OK", [('Content-type', 'text/plain')])
        return [b'Hello World, This could be a CE Application !']
