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
    ['query_capability', 'creation_factory', 'selection_dialog', 'creation_dialog']
)


class Provider(object):
    methods = None

    def generate(self):
        raise NotImplementedError()

    @classmethod
    def as_provider(cls, name, *class_args, **class_kwargs):

        def provider(*args, **kwargs):
            self = provider.provider_class(*class_args, **class_kwargs)
            return self.generate(*args, **kwargs)

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
    representations = None
    domain = None
    type = None
    service_path = None

    def __init__(self, api=None, *args, **kwargs):
        self.api = api

    def generate(self, *args, **kwargs):
        # Taken from flask
        meth = getattr(self, 'query_capability', None)
        if meth is None and request.method == "HEAD":
            meth = getattr(self, "query_capability", None)
        assert meth is not None, "Unimplemented method %r" % request.method

        resp = meth(*args, **kwargs)

        if isinstance(resp, list):
            return resp

        representations = self.representations or {}

        mediatype = request.accept_mimetypes.best_match(representations, default=None)
        if mediatype in representations:
            data, code, headers = unpack(resp)
            resp = representations[mediatype](data, code, headers)
            resp.headers["Content-Type"] = mediatype
            return resp

        return resp
