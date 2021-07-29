from collections import namedtuple

from rdflib import Graph, URIRef, RDF, RDFS, DCTERMS, Literal, XSD
from rdflib.resource import Resource
from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map

from pyoslc.vocabularies.core import OSLC
from pyoslc_server.context import Context
from pyoslc_server.wrappers import Response

ResourceRoute = namedtuple("ResourceRoute", "resource urls kwargs")


class OSLCAPI:

    # url_rule_class = Rule

    def __init__(self, path, prefix="", **kwargs):
        self.path = path
        self.view_functions = {}
        self.url_map = Map()
        self.resources = []

        self.graph = Graph()
        self.graph.bind('oslc', OSLC)
        self.graph.bind('rdf', RDF)
        self.graph.bind('rdfs', RDFS)
        self.graph.bind('dcterms', DCTERMS)

    def add_resource(self, resource, *urls, **kwargs):
        self.resources.append(ResourceRoute(resource, urls, kwargs))

    def handle_exception(self, error):
        if isinstance(error, HTTPException):
            return error

    def dispatch_request(self, context):
        request = context.request
        if request.routing_exception is not None:
            raise request.routing_exception

        rule = request.url_rule
        return self.view_functions[rule.endpoing](**request.view_args)

    def full_dispatch_request(self, context):
        try:
            res = self.dispatch_request(context)
        except Exception as e:
            res = self.handle_exception(e)

        return self.finalize_request(res, context.request)

    def finalize_request(self, res, request):
        response = self.make_response(res, request)
        return response

    def make_response(self, response, request):
        # status = headers = None

        if not isinstance(response, Response):
            r = Resource(self.graph, URIRef(request.url_root))
            r.add(RDF.type, OSLC.Error)
            r.add(OSLC.statusCode, Literal(response.code))
            r.add(OSLC.message, Literal(response.description, datatype=XSD.string))

            response = Response(self.graph.serialize(), status=response.code, mimetype='application/rdf+xml')

        return response

    def get_adapter(self, request):
        return self.url_map.bind_to_environ(request.environ)

    def get_context(self, environ):
        return Context(self, environ)

    def wsgi_check(self, environ):
        if environ['PATH_INFO'].startswith(self.path):
            return True

        return False

    def wsgi_app(self, environ, start_response):
        context = self.get_context(environ)
        try:
            response = self.full_dispatch_request(context=context)
        except Exception as e:
            response = self.handle_exception(e)

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
