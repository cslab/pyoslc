from pyoslc_server import OSLCAPP

from apposlc.adapter import RequirementAdapter, REQ_TO_RDF
from apposlc.resource import REQSTORE


class OSLCEnabled:

    def __init__(self):
        self.app = OSLCAPP(prefix='/oslc')

        self.app.api.add_provider(catalog_id='catalog',
                                  provider_id='Project-1',
                                  title='PyOSLC Service Provider for Project 1',
                                  description='Service Provider',
                                  adapter=RequirementAdapter)

        req_data = RequirementAdapter(REQSTORE)
        self.app.add_url_rule(
            "/requirements/<string:identifier>",
            view_func=req_data.get_item,
            attr_mapping=REQ_TO_RDF,
            rdf_type=req_data.type,
            oslc_domain=req_data.domain,
        )

    def __call__(self, environ, start_response):
        """
        Callable function required
        """

        if self.app.wsgi_check(environ):
            return self.app(environ, start_response)

        start_response("200 OK", [('Content-type', 'text/plain')])
        return [b'Hello World, This could be a CE Application !']
