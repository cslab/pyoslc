from __future__ import absolute_import

import sys

from six import reraise, text_type
from werkzeug.datastructures import Headers
from werkzeug.exceptions import HTTPException, InternalServerError, BadRequestKeyError, NotFound, \
    UnsupportedMediaType, NotImplemented
from werkzeug.routing import Map, Rule
from werkzeug.routing import RoutingException
from werkzeug.wrappers import BaseResponse

from .api import API
from .context import Context, AppContext
from .wrappers import Response
from .globals import _request_ctx_stack, request
from .rdf import to_rdf
from .exceptions import OSLCException
from .logging import create_logger


class OSLCAPP:

    DEFAULT_FORMAT = "text/turtle"

    testing = False

    def __init__(self, name="oslc-app", prefix="/oslc", **kwargs):
        self.name = name
        self.prefix = prefix
        self.view_functions = {}
        self.view_mappings = {}
        self.rdf_type = {}
        self.oslc_domain = {}
        self.url_map = Map()
        self.rdf_format = self.DEFAULT_FORMAT
        self.accept = self.DEFAULT_FORMAT
        self._debug = True

        self.logger = create_logger(self)

        self.logger.debug('Initializing OSLC APP: <name: {name}> <prefix: {prefix}>'.format(name=name, prefix=prefix))
        self.api = API(self, '/services')

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = value

    def logger(self):
        return create_logger(self)

    def test_client(self, use_cookies=True, **kwargs):
        from .testing import OSLCAPPClient
        return OSLCAPPClient(self, Response, use_cookies=use_cookies, **kwargs)

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

        rule = Rule(self.prefix + rule, methods=methods, **options)

        self.url_map.add(rule)
        if view_func is not None:
            old_func = self.view_functions.get(endpoint)
            if old_func is not None and old_func != view_func:
                raise AssertionError('View function mapping is overwriting an '
                                     'existing endpoint function: %s' % endpoint)
            self.view_functions[endpoint] = view_func

    def handle_http_exception(self, error):
        if error.code is None:
            return error

        if isinstance(error, RoutingException):
            return error

        if isinstance(error, NotFound) or isinstance(error, UnsupportedMediaType) or isinstance(error, NotImplemented):
            return error

        return self.handle_exception(error)

    def handle_user_exception(self, error):

        exc_type, exc_value, tb = sys.exc_info()
        assert exc_value is error

        if isinstance(error, BadRequestKeyError):
            if not hasattr(BadRequestKeyError, "show_exception"):
                error.args = ()

        if isinstance(error, HTTPException):
            return self.handle_http_exception(error)

        reraise(exc_type, exc_value, tb)

    def handle_exception(self, error):
        exc_type, exc_value, tb = sys.exc_info()
        if exc_value is error:
            reraise(exc_type, exc_value, tb)

        server_error = InternalServerError()
        server_error.original_exception = error
        return self.finalize_request(server_error)

    def preprocess_request(self):
        request = _request_ctx_stack.top.request

        if not(request.accept_mimetypes.best in ('*/*', 'text/html')):
            self.accept = request.accept_mimetypes.best
            self.rdf_format = self.accept

        if not (self.accept in ('application/rdf+xml', 'application/json',
                                'application/ld+json', 'application/json-ld',
                                'application/xml', 'application/atom+xml',
                                'text/turtle',
                                'application/xml, application/x-oslc-cm-service-description+xml',
                                'application/x-oslc-compact+xml, application/x-jazz-compact-rendering; q=0.5',
                                'application/rdf+xml,application/x-turtle,application/ntriples,application/json')):
            self.rdf_format = request.content_type
            self.accept = request.content_type
            raise UnsupportedMediaType

        if not request.content_type:
            request.content_type = self.accept

        if self.accept in ('application/json-ld', 'application/ld+json', 'application/json'):
            # If the content-type is any kind of json,
            # we will use the json-ld format for the response.
            self.rdf_format = 'json-ld'

        if self.accept in ('application/xml', 'application/rdf+xml', 'application/atom+xml'):
            self.rdf_format = 'pretty-xml'

    def dispatch_request(self):
        request = _request_ctx_stack.top.request

        if request.routing_exception is not None:
            raise request.routing_exception

        rule = request.url_rule
        return self.view_functions[rule.endpoint](**request.view_args)

    def full_dispatch_request(self):
        try:
            res = self.preprocess_request()
            if not res:
                res = self.dispatch_request()
        except Exception as e:
            res = self.handle_user_exception(e)

        return self.finalize_request(res)

    def finalize_request(self, res):
        response = self.make_response(res)
        return response

    def make_response(self, response):
        status = headers = None

        if response is None:
            raise TypeError(
                "The view function did not return a valid response. The"
                " function either returned None or ended without a return"
                " statement."
            )

        if isinstance(response, HTTPException):
            error = OSLCException(about=request.base_url, status_code=response.code, message=response.description)
            response = error.to_rdf()
            response = Response(response.serialize(format=self.rdf_format),
                                status=error.status_code,
                                content_type=self.accept,
                                mimetype=self.accept)
            status = headers = None
        elif not isinstance(response, Response):
            if isinstance(response, (text_type, bytes, bytearray)):
                # let the response class set the status and headers instead of
                # waiting to do it manually, so that the class can handle any
                # special logic
                response = Response(response, status=status, headers=headers)
                status = headers = None
            elif isinstance(response, dict):
                rdf_type = self.rdf_type[request.url_rule.endpoint]
                oslc_domain = self.oslc_domain[request.url_rule.endpoint]
                attr_mapping = self.view_mappings[request.url_rule.endpoint]
                response = to_rdf(request.base_url, attr_mapping, rdf_type, oslc_domain, self.rdf_format, response)
                response = Response(response, status=status, headers=headers)
                status = headers = None
            elif isinstance(response, BaseResponse) or callable(response):
                # evaluate a WSGI callable, or coerce a different response
                # class to the correct type
                try:
                    response = Response.force_type(response, request.environ)
                except TypeError as e:
                    new_error = TypeError(
                        "{e}\nThe view function did not return a valid"
                        " response. The return type must be a string, dict, tuple,"
                        " Response instance, or WSGI callable, but it was a"
                        " {rv.__class__.__name__}.".format(e=e, rv=response)
                    )
                    reraise(TypeError, new_error, sys.exc_info()[2])

            if isinstance(response, object):  # dictionary
                rdf_type = self.rdf_type[request.url_rule.endpoint]
                oslc_domain = self.oslc_domain[request.url_rule.endpoint]
                attr_mapping = self.view_mappings[request.url_rule.endpoint]
                response = to_rdf(request.base_url, attr_mapping, rdf_type, oslc_domain, self.rdf_format, response)
                response = Response(response, status=status, headers=headers)
                status = headers = None

        if not('OSLC-Core-Version' in response.headers.keys()):
            headers = Headers([('OSLC-Core-Version', '2.0')])
            response.headers.extend(headers)

        return response

    def do_teardown_appcontext(self, exc=object()):
        """Called right before the application context is popped.

        When handling a request, the application context is popped
        after the request context. See :meth:`do_teardown_request`.

        This calls all functions decorated with
        :meth:`teardown_appcontext`. Then the
        :data:`appcontext_tearing_down` signal is sent.

        This is called by
        :meth:`AppContext.pop() <flask.ctx.AppContext.pop>`.

        .. versionadded:: 0.9
        """
        if exc is object():
            exc = sys.exc_info()[1]        

    def app_context(self):
        return AppContext(self)

    def get_adapter(self, request):
        if request is not None:
            return self.url_map.bind_to_environ(request.environ)

        return self.url_map.bind(
            'localhost',
            script_name=self.name,
            url_scheme='http',
        )

    def get_context(self, environ):
        return Context(self, environ)

    def wsgi_check(self, environ):
        if environ['PATH_INFO'].startswith(self.prefix):
            return True

        return False

    def wsgi_app(self, environ, start_response):
        context = self.get_context(environ)
        try:
            try:
                context.push()
                response = self.full_dispatch_request()
            except Exception as e:
                response = self.handle_exception(e)
            return response(environ, start_response)
        finally:
            context.pop()

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
