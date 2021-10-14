from __future__ import absolute_import

from collections import OrderedDict
from functools import wraps

from werkzeug.exceptions import NotAcceptable, InternalServerError
from werkzeug.wrappers import Response

from .namespace import Namespace
from .endpoints import ServiceProviderCatalog, ServiceProvider, ResourceListOperation, ResourceItemOperation
from .helpers import camel_to_dash
from .views import unpack
from .globals import request
from .helpers import make_response as oslcapp_make_response
from .rdf import to_rdf

DEFAULT_REPRESENTATIONS = [("text/turtle", to_rdf)]


class API(object):

    def __init__(self, app=None, authorizations=None, prefix="/services", **kwargs):
        self.app = app
        self.namespaces = []
        self.ns_paths = dict()
        self.prefix = prefix
        self.endpoints = set()
        self.default_mediatype = 'text/turtle'

        self.authorizations = authorizations
        self.representations = OrderedDict(DEFAULT_REPRESENTATIONS)

        app.logger.debug(
            'Initializing OSLC API: <name: {name}> <prefix: {prefix}>'.format(name=app.name, prefix=self.prefix)
        )

        self.default_namespace = self._namespace(title='catalog', description='Service Provider Catalog')
        self.default_namespace.add_resource(ServiceProviderCatalog, '/catalog')

    def _complete_url(self, url_part, registration_prefix):
        parts = (registration_prefix, self.prefix, url_part)
        return "".join(part for part in parts if part)

    def register_resource(self, namespace, resource, *urls, **kwargs):
        endpoint = kwargs.pop("endpoint", None)
        endpoint = str(endpoint or self.default_endpoint(resource, namespace))

        self.app.logger.debug(
            'Registering endpoint: <{endpoint}> resource: <{resource}> '.format(resource=resource.__name__,
                                                                                endpoint=endpoint)
        )
        kwargs["endpoint"] = endpoint
        self.endpoints.add(endpoint)

        if self.app is not None:
            self._register_view(self.app, resource, namespace, *urls, **kwargs)

        return endpoint

    def register_adapter(self, namespace, adapter, *urls, **kwargs):
        endpoint = kwargs.pop("endpoint", None)
        endpoint = str(endpoint or self.default_endpoint(adapter.__class__, namespace))
        # if self.app is not None:
        #     self._register_oslc_adapter(self.app, resource, namespace, *urls, **kwargs)
        return True

    def _register_view(self, app, resource, namespace, *urls, **kwargs):
        endpoint = kwargs.pop("endpoint", None) or camel_to_dash(resource.__name__)
        resource_class_args = kwargs.pop("resource_class_args", ())
        resource_class_kwargs = kwargs.pop("resource_class_kwargs", {})

        if endpoint in getattr(app, "view_functions", {}):
            previous_view_class = app.view_functions[endpoint].__dict__["view_class"]

            # if you override the endpoint with a different class, avoid the
            # collision by raising an exception
            if previous_view_class != resource:
                msg = "This endpoint (%s) is already set to the class %s."
                raise ValueError(msg % (endpoint, previous_view_class.__name__))

        resource.endpoint = endpoint

        resource_func = self.output(
            resource.as_view(
                endpoint, self, namespace=namespace, *resource_class_args, **resource_class_kwargs
            )
        )

        for url in urls:
            rule = self._complete_url(url, "")
            # Add the url to the application
            self.app.logger.debug(
                "Adding <rule: {rule}> <view_func: {resource_func}>".format(
                    rule=rule, resource_func=resource_func.__name__)
            )
            app.add_url_rule(rule, view_func=resource_func,  **kwargs)

    def _register_oslc_adapter(self):
        pass

    def output(self, resource):

        @wraps(resource)
        def wrapper(*args, **kwargs):
            resp = resource(*args, **kwargs)
            if isinstance(resp, Response):
                return resp
            data, code, headers = unpack(resp)
            return self.make_response(data, code, headers=headers)

        return wrapper

    def output_provider(self, resource):

        @wraps(resource)
        def wrapper(oslc_method, *args, **kwargs):
            resp = resource(oslc_method, *args, **kwargs)
            return resp
            # if isinstance(resp, BaseResponse):
            #     return resp
            # data, code, headers = unpack(resp)
            # return self.make_response(data, code, headers=headers)

        return wrapper

    def make_response(self, data, *args, **kwargs):
        default_mediatype = (
                kwargs.pop("fallback_mediatype", None) or self.default_mediatype
        )
        mediatype = request.accept_mimetypes.best_match(
            self.representations, default=default_mediatype,
        )
        if mediatype is None:
            raise NotAcceptable()
        if mediatype in self.representations:
            resp = self.representations[mediatype](data, *args, **kwargs)
            resp.headers["Content-Type"] = mediatype
            return resp
        elif mediatype == "text/plain":
            resp = oslcapp_make_response(str(data), *args, **kwargs)
            resp.headers["Content-Type"] = "text/plain"
            return resp
        else:
            raise InternalServerError()

    def default_endpoint(self, resource, namespace):
        endpoint = camel_to_dash(resource.__name__)
        if namespace is not self.default_namespace:
            endpoint = "{ns.title}_{endpoint}".format(ns=namespace, endpoint=endpoint)
        if endpoint in self.endpoints:
            suffix = 2
            while True:
                new_endpoint = "{base}_{suffix}".format(base=endpoint, suffix=suffix)
                if new_endpoint not in self.endpoints:
                    endpoint = new_endpoint
                    break
                suffix += 1
        return endpoint

    def get_ns_path(self, ns):
        return self.ns_paths.get(ns)

    def ns_urls(self, ns, urls):
        path = self.get_ns_path(ns) or ns.path
        return [path + url for url in urls]

    def _add_namespace(self, ns, path=None):
        if ns not in self.namespaces:
            self.app.logger.debug("Adding namespace: <{namespace}>".format(namespace=ns.title))
            self.namespaces.append(ns)
            if path is not None:
                self.ns_paths[ns] = path

    def _namespace(self, *args, **kwargs):
        ns = Namespace(api=self, *args, **kwargs)
        self._add_namespace(ns)
        return ns

    def add_adapter(self, adapter):
        self.app.logger.debug("Adding adapter: <{adapter}>".format(adapter=adapter.identifier))
        self.default_namespace.add_resource(ServiceProvider, '/provider/<string:provider_id>')
        self.default_namespace.add_resource(ResourceListOperation, '/provider/<string:provider_id>/resources')
        self.default_namespace.add_resource(ResourceItemOperation,
                                            '/provider/<string:provider_id>/resources/<string:resource_id>')
        self.default_namespace.add_adapter(adapter)
