from rdflib import DCTERMS

from pyoslc_server import OSLCAPP

from apposlc.adapter import RequirementAdapter, TestCaseAdapter, REQ_TO_RDF


class OSLCEnabled:

    def __init__(self):
        self.app = OSLCAPP(prefix='/oslc')
        self.app.api.add_adapter(
            identifier='adapter',
            title='Requirement Adapter',
            description='Requirement Adapter for OSLC',
            klass=RequirementAdapter,
            mapping=REQ_TO_RDF,
        )

        self.app.api.add_adapter(
            'tests',
            'test cases',
            'test cases',
            TestCaseAdapter,
            {
                "identifier": DCTERMS.identifier,
                "title": DCTERMS.title,
                "description": DCTERMS.description,
            },
        )

    def __call__(self, environ, start_response):
        """
        Callable function required
        """

        if self.app.wsgi_check(environ):
            return self.app(environ, start_response)

        start_response("200 OK", [('Content-type', 'text/plain')])
        return [b'Hello World, This could be a CE Application !']
