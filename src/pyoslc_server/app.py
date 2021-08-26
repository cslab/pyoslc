import logging
import sys

from werkzeug._compat import integer_types, reraise, text_type
from werkzeug.datastructures import Headers
from werkzeug.exceptions import HTTPException, InternalServerError, BadRequestKeyError, default_exceptions, NotFound
from werkzeug.routing import Map
from werkzeug.routing import Rule
from werkzeug.routing import RoutingException
from werkzeug.wrappers import BaseResponse

from .api import API
from .context import Context
from .wrappers import Response
from .globals import _request_ctx_stack, request
from .rdf import to_rdf
from .exceptions import OSLCException

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter('%(asctime)s '
                                              '%(levelname)s: %(message)s '))


class OSLCAPP:

    def __init__(self, name="oslc-app", prefix="oslc", **kwargs):
        self.name = name
        self.prefix = prefix
        self.view_functions = {}
        self.view_mappings = {}
        self.rdf_type = {}
        self.oslc_domain = {}
        self.url_map = Map()

        self.rdf_format = 'text/turtle'
        self.accept = 'text/turtle'

        self.error_handler_spec = {}

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(stream_handler)

        self.logger.debug('Initializing OSLC APP: <name: {name}> <prefix: {prefix}>'.format(name=name, prefix=prefix))
        self.api = API(self, '/services')

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):

        self.logger.debug("<rule: {rule}> <endpoint: {endpoint}> <view_func: {view_func}> <options: {options}>".format(
            rule=rule, endpoint=endpoint, view_func=view_func, options=options))

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

    @staticmethod
    def _get_exc_class_and_code(exc_class_or_code):
        """Get the exception class being handled. For HTTP status codes
        or ``HTTPException`` subclasses, return both the exception and
        status code.

        :param exc_class_or_code: Any exception class, or an HTTP status
            code as an integer.
        """
        if isinstance(exc_class_or_code, integer_types):
            exc_class = default_exceptions[exc_class_or_code]
        else:
            exc_class = exc_class_or_code

        assert issubclass(exc_class, Exception)

        if issubclass(exc_class, HTTPException):
            return exc_class, exc_class.code
        else:
            return exc_class, None

    def _find_error_handler(self, error):
        exc_class, code = self._get_exc_class_and_code(type(error))

        for name, c in (
                (request.url_rule.endpoint, code),
                (None, code),
                (request.url_rule.endpoint, None),
                (None, None),
        ):
            handler_map = self.error_handler_spec.setdefault(name, {}).get(c)

            if not handler_map:
                continue

            for cls in exc_class.__mro__:
                handler = handler_map.get(cls)

                if handler is not None:
                    return handler

    def handle_http_exception(self, error):
        if error.code is None:
            return error

        if isinstance(error, RoutingException):
            return error

        if isinstance(error, NotFound):
            return error

        handler = self._find_error_handler(error)
        if handler is None:
            return error

        return handler(error)

    def handle_user_exception(self, error):

        exc_type, exc_value, tb = sys.exc_info()
        assert exc_value is error

        if isinstance(error, BadRequestKeyError):
            if not hasattr(BadRequestKeyError, "show_exception"):
                error.args = ()

        if isinstance(error, HTTPException):
            return self.handle_http_exception(error)

        handler = self._find_error_handler(error)
        if handler is None:
            reraise(exc_type, exc_value, tb)

        return handler(error)

    def handle_exception(self, error):

        server_error = InternalServerError()
        server_error.original_exception = error
        handler = self._find_error_handler(server_error)

        if handler is not None:
            server_error = handler(server_error)

        return self.finalize_request(server_error)  # , from_error_handler=True)

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
            res = self.handle_user_exception(e)

        return self.finalize_request(res)

    def finalize_request(self, res):
        response = self.make_response(res)
        return response

    def make_response(self, response):
        status = headers = None
        
        if isinstance(response, HTTPException):
            error = OSLCException(about=request.base_url, status_code=response.code, message=response.description)
            response = error.to_rdf()
            response = Response(response.serialize(format=self.rdf_format),
                                status=error.status_code,
                                mimetype='text/turtle')
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
