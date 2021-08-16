import logging

from rdflib import Graph, URIRef, RDF, Literal, XSD, RDFS, DCTERMS
from rdflib.resource import Resource
from werkzeug.datastructures import Headers
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.routing import Map
from werkzeug.routing import Rule

from pyoslc.vocabularies.core import OSLC
from .api import API
from .context import Context
from .wrappers import Response
from .globals import _request_ctx_stack
from .rdf import to_rdf


class OSLCAPP:

    def __init__(self, name="oslc-app", prefix="oslc", **kwargs):
        self.name = name
        self.prefix = prefix
        self.view_functions = {}
        self.view_mappings = {}
        self.rdf_type = {}
        self.oslc_domain = {}
        self.url_map = Map()

        self.graph = Graph()
        self.graph.bind('oslc', OSLC)
        self.graph.bind('rdf', RDF)
        self.graph.bind('rdfs', RDFS)
        self.graph.bind('dcterms', DCTERMS)
        self.rdf_format = 'text/turtle'
        self.accept = 'text/turtle'
        self.default_mediatype = 'application/json'

        self.api = API(self, '{prefix}/service/catalog'.format(prefix=self.prefix))

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):

        if endpoint is None:
            assert view_func is not None, 'expected view func if endpoint ' \
                                          'is not provided.'
            endpoint = view_func.__name__

        options['endpoint'] = endpoint
        methods = options.pop('methods', None)

        # if the methods are not given and the view_func object knows its
        # methods we can use that instead.  If neither exists, we go with
        # a tuple of only ``GET`` as default.
        if methods is None:
            methods = getattr(view_func, 'methods', None) or ('GET',)
        if isinstance(methods, str):
            raise TypeError('Allowed methods have to be iterables of strings, '
                            'for example: @app.route(..., methods=["POST"])')
        methods = set(item.upper() for item in methods)

        # Methods that should always be added
        required_methods = set(getattr(view_func, 'required_methods', ()))

        # Add the required methods now.
        methods |= required_methods

        rdf_type = options.pop('rdf_type', None)
        oslc_domain = options.pop('oslc_domain', None)
        attr_mapping = options.pop('attr_mapping', None)

        rule = Rule(self.prefix + rule, methods=methods, **options)

        self.url_map.add(rule)
        if view_func is not None:
            old_func = self.view_functions.get(endpoint)
            if old_func is not None and old_func != view_func:
                raise AssertionError('View function mapping is overwriting an '
                                     'existing endpoint function: %s' % endpoint)
            self.view_functions[endpoint] = view_func
            self.view_mappings[endpoint] = attr_mapping
            self.rdf_type[endpoint] = rdf_type
            self.oslc_domain[endpoint] = oslc_domain

    def handle_exception(self, error):
        if isinstance(error, HTTPException):
            return error

        return InternalServerError()

    def preprocess_request(self, request):
        accept = request.accept_mimetypes

        if accept.best == '*/*' and not request.content_type:
            request.content_type = accept

        if accept in ('application/json-ld', 'application/ld+json', 'application/json'):
            # If the content-type is any kind of json,
            # we will use the json-ld format for the response.
            self.rdf_format = 'json-ld'

        if accept in ('application/xml', 'application/rdf+xml', 'application/atom+xml'):
            self.rdf_format = 'pretty-xml'

        return None

    def dispatch_request(self, context):
        request = context.request
        req = _request_ctx_stack.top.request

        if request.routing_exception is not None:
            raise request.routing_exception

        rule = request.url_rule
        return self.view_functions[rule.endpoint](**request.view_args)

    def full_dispatch_request(self, context):
        try:
            res = self.preprocess_request(context.request)
            if not res:
                res = self.dispatch_request(context)
        except Exception as e:
            res = self.handle_exception(e)

        return self.finalize_request(res, context.request)

    def finalize_request(self, res, request):
        response = self.make_response(res, request)
        return response

    def make_response(self, response, request):
        status = headers = None

        if not isinstance(response, Response):
            if isinstance(response, object):
                rdf_type = self.rdf_type[request.url_rule.endpoint]
                oslc_domain = self.oslc_domain[request.url_rule.endpoint]
                attr_mapping = self.view_mappings[request.url_rule.endpoint]
                response = to_rdf(request.base_url, attr_mapping, rdf_type, oslc_domain, self.rdf_format, response)
                response = Response(response, status=status, headers=headers)
                status = headers = None

            elif isinstance(response, (Graph)):
                response = Response(response.serialize(format=self.rdf_format),
                                    status=200,
                                    mimetype='text/turtle')
            else:
                r = Resource(self.graph, URIRef(request.url_root))
                r.add(RDF.type, OSLC.Error)
                r.add(OSLC.statusCode, Literal(response.code))
                r.add(OSLC.message, Literal(response.description, datatype=XSD.string))

                response = Response(self.graph.serialize(format=self.rdf_format),
                                    status=response.code,
                                    mimetype=request.content_type)

        headers = Headers([('OSLC-Core-Version', '2.0')])
        response.headers.extend(headers)

        return response

    def get_adapter(self, request):
        return self.url_map.bind_to_environ(request.environ)

    def get_context(self, environ):
        return Context(self, environ)

    def wsgi_check(self, environ):
        if environ['PATH_INFO'].startswith(self.prefix):
            return True

        return False

    def wsgi_app(self, environ, start_response):
        context = self.get_context(environ)
        try:
            top = _request_ctx_stack.top
            if top is not None and top.preserved:
                _request_ctx_stack.pop()

            _request_ctx_stack.push(context)

            response = self.full_dispatch_request(context=context)
        except Exception as e:
            response = self.handle_exception(e)

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
