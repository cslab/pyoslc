import operator

import six

from functools import wraps

from werkzeug.exceptions import NotAcceptable, InternalServerError
from werkzeug.wrappers import BaseResponse

from .namespace import Namespace
from .endpoints import ServiceProviderCatalog, ServiceProvider
from .helpers import camel_to_dash
from .views import unpack
from .globals import request
from .helpers import make_response as oslcapp_make_response


class API(object):

    def __init__(self, app=None, prefix="/services", **kwargs):
        self.namespaces = []
        self.ns_paths = dict()
        self.urls = {}
        self.prefix = prefix
        self.endpoints = set()
        self.resources = []
        self.app = None
        self.default_mediatype = 'text/turtle'

        self.default_namespace = None

        if app is not None:
            self.app = app
            self.init_app(app)

        app.logger.debug(
            'Initializing OSLC API: <name: {name}> <prefix: {prefix}>'.format(name=app.name, prefix=self.prefix))

        self.default_namespace = self._namespace(title='catalog', description='Service Provider Catalog')

    def init_app(self, app, **kwargs):
        self.app = app

        if len(self.resources) > 0:
            for resource, namespace, urls, kwargs in self.resources:
                self._register_view(app, resource, namespace, *urls, **kwargs)

    def __getattr__(self, name):
        try:
            return getattr(self.default_namespace, name)
        except AttributeError:
            raise AttributeError("Api does not have {0} attribute".format(name))

    def _complete_url(self, url_part, registration_prefix):
        parts = (registration_prefix, self.prefix, url_part)
        return "".join(part for part in parts if part)

    def register_resource(self, namespace, resource, *urls, **kwargs):
        endpoint = kwargs.pop("endpoint", None)
        endpoint = str(endpoint or self.default_endpoint(resource, namespace))

        kwargs["endpoint"] = endpoint
        self.endpoints.add(endpoint)

        if self.app is not None:
            self._register_view(self.app, resource, namespace, *urls, **kwargs)
        else:
            self.resources.append((resource, namespace, urls, kwargs))

        return endpoint

    def _register_view(self, app, resource, namespace, *urls, **kwargs):
        self.app.logger.debug(
            'Register: <namespace: {name}> <resource: {resource}> <urls: {urls}> <kwargs: {kwargs}>'.format(
                name=namespace.name, resource=resource.__name__, urls=urls, kwargs=kwargs))
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

        resource.mediatypes = self.mediatypes_method()  # Hacky
        resource.endpoint = endpoint

        resource_func = self.output(
            resource.as_view(
                endpoint, self, *resource_class_args, **resource_class_kwargs
            )
        )

        # Apply Namespace and Api decorators to a resource
        # for decorator in chain(namespace.decorators, self.decorators):
        #     resource_func = decorator(resource_func)

        for url in urls:
            rule = self._complete_url(url, "")
            # Add the url to the application
            app.add_url_rule(rule, view_func=resource_func, **kwargs)

    def output(self, resource):

        @wraps(resource)
        def wrapper(*args, **kwargs):
            resp = resource(*args, **kwargs)
            if isinstance(resp, BaseResponse):
                return resp
            data, code, headers = unpack(resp)
            return self.make_response(data, code, headers=headers)

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
            endpoint = "{ns.name}_{endpoint}".format(ns=namespace, endpoint=endpoint)
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
        self.app.logger.debug("Adding Namespace: <name: {name}> <path: {path}>".format(name=ns.name, path=path))
        if ns not in self.namespaces:
            self.namespaces.append(ns)
            if self not in ns.apis:
                ns.apis.append(self)
            # Associate ns with prefix-path
            if path is not None:
                self.ns_paths[ns] = path

        for r in ns.resources:
            urls = self.ns_urls(ns, r.urls)
            self.register_resource(ns, r.resource, *urls, **r.kwargs)
        # Register models
        for name, definition in six.iteritems(ns.models):
            self.models[name] = definition

    def _namespace(self, *args, **kwargs):
        name = kwargs.get('title', None)
        ns = Namespace(name=name, api=self, *args, **kwargs)
        self._add_namespace(ns)
        ns.add_resource(ServiceProviderCatalog, '/catalog', resource_class_kwargs=kwargs)
        return ns

    def add_provider(self, catalog_id, *args, **kwargs):
        ns = self.namespaces[[a.name for a in self.namespaces].index(catalog_id)]
        # kwargs.update({'provider': ns.resources})
        provider_id = kwargs.get('provider_id', None)
        name = kwargs.get('title', None)
        description = kwargs.get('description', None)
        kwargs.update({'providers': [{
            'id': provider_id,
            'name': name,
            'description': description,
        }]})
        ns.add_resource(ServiceProvider, '/provider/<string:provider_id>', resource_class_kwargs=kwargs)
        return ns

    def mediatypes_method(self):
        """Return a method that returns a list of mediatypes"""
        return lambda resource_cls: self.mediatypes() + [self.default_mediatype]

    def mediatypes(self):
        """Returns a list of requested mediatypes sent in the Accept header"""
        # 'application/json',
        return [
            h
            for h, q in sorted(
                request.accept_mimetypes, key=operator.itemgetter(1), reverse=True
            )
        ]
