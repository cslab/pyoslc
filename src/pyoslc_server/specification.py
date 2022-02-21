from .globals import request
from .utils import unpack


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""

    # This requires a bit of explanation: the basic idea is to make a
    # dummy metaclass for one level of class instantiation that replaces
    # itself with the actual metaclass.
    class metaclass(type):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)

    return type.__new__(metaclass, 'temporary_class', (), {})


method_funcs = frozenset(
    ['query_capability', 'creation_factory', 'selection_dialog', 'creation_dialog', 'get_resource']
)


class Provider(object):
    methods = None

    def generate(self):
        raise NotImplementedError()

    @classmethod
    def as_provider(cls, name, *class_args, **class_kwargs):

        def provider(oslc_method, *args, **kwargs):
            self = provider.provider_class(*class_args, **class_kwargs)
            return self.generate(oslc_method, *args, **kwargs)

        provider.provider_class = cls
        provider.__name__ = name
        provider.__doc__ = cls.__doc__
        provider.__module__ = cls.__module__
        provider.methods = cls.methods
        return provider


class ProviderResource(type):

    def __init__(cls, name, bases, d):
        super(ProviderResource, cls).__init__(name, bases, d)

        if 'methods' not in d:
            methods = set()

            for key in method_funcs:
                if hasattr(cls, key):
                    methods.add(key.upper())

            if methods:
                cls.methods = methods


class ServiceResource(with_metaclass(ProviderResource, Provider)):

    def generate(self, *args, **kwargs):
        method = getattr(self, request.method.lower(), None)

        if method is None:
            method = getattr(self, 'query_capability', None)

        assert method is not None, 'Unimplemented method %r' % method
        return method(*args, **kwargs)


class ServiceResourceAdapter(ServiceResource):
    identifier = None
    title = None
    description = None
    representations = None
    domain = None
    service_path = 'provider/{id}/resources'

    def __init__(self, identifier, title, mapping=None, **kwargs):
        self.identifier = identifier
        self.title = title
        self.description = kwargs.get('description', '')
        self.types = None

    @property
    def types(self):
        return self.__types

    @types.setter
    def types(self, types):
        self.__types = types

    def add_type(self, resource_type):
        if resource_type:
            self.types.append(resource_type)

    def generate(self, oslc_method, *args, **kwargs):
        meth = getattr(self, oslc_method, None)
        assert meth is not None, "Unimplemented method {} in {}".format(oslc_method.lower(), self.__class__.__name__)

        resp = meth(**kwargs)

        if isinstance(resp, list) or isinstance(resp, object) or isinstance(resp, dict):
            return resp

        representations = self.representations or {}

        mediatype = request.accept_mimetypes.best_match(representations, default=None)
        if mediatype in representations:
            data, code, headers = unpack(resp)
            resp = representations[mediatype](data, code, headers)
            resp.headers["Content-Type"] = mediatype
            return resp

        return resp
