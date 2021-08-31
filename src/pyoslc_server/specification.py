# from pyoslc.vocabularies.jazz import JAZZ_CONFIG
from werkzeug.wrappers import BaseResponse

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


method_funcs = frozenset(['creation_factory',
                          'query_capability',
                          'creation_dialog',
                          'selection_dialog'])


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
    # domain = None
    domain = 'http://open-services.net/ns/rm#'
    # service_path = None
    service_path = 'provider/{id}/resources'

    def __init__(self, api=None, *args, **kwargs):
        self.api = api

    # @staticmethod
    # def query_capability():
    #     return {
    #         'title': 'Query Capability',
    #         'label': 'Query Capability',
    #         'resource_shape': 'resourceShapes/requirement',
    #         'resource_type': ['http://open-services.net/ns/rm#Requirement'],
    #         'usages': []
    #     }
    #
    # @staticmethod
    # def creation_factory():
    #     return {
    #         'title': 'Creation Factory',
    #         'label': 'Creation Factory',
    #         'resource_shape': ['resourceShapes/requirement'],
    #         'resource_type': ['http://open-services.net/ns/rm#Requirement'],
    #         'usages': []
    #     }
    #
    # @staticmethod
    # def selection_dialog():
    #     return {
    #         'title': 'Selection Dialog',
    #         'label': 'Selection Dialog Service',
    #         'uri': 'provider/{id}/resources/selector',
    #         'hint_width': '525px',
    #         'hint_height': '325px',
    #         'resource_type': ['http://open-services.net/ns/cm#ChangeRequest',
    #                           'http://open-services.net/ns/am#Resource',
    #                           'http://open-services.net/ns/rm#Requirement'],
    #         'usages': ['http://open-services.net/ns/am#PyOSLCSelectionDialog']
    #     }
    #
    # @staticmethod
    # def creation_dialog():
    #     return {
    #         'title': 'Creation Dialog',
    #         'label': 'Creation Dialog service',
    #         'uri': 'provider/{id}/resources/creator',
    #         'hint_width': '525px',
    #         'hint_height': '325px',
    #         'resource_shape': 'resourceShapes/eventType',
    #         'resource_type': ['http://open-services.net/ns/cm#ChangeRequest',
    #                           'http://open-services.net/ns/am#Resource',
    #                           'http://open-services.net/ns/rm#Requirement'],
    #         'usages': ['http://open-services.net/ns/am#PyOSLCCreationDialog']
    #     }

    def generate(self, *args, **kwargs):
        # Taken from flask
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == "HEAD":
            meth = getattr(self, "get", None)
        assert meth is not None, "Unimplemented method %r" % request.method

        resp = meth(*args, **kwargs)

        if isinstance(resp, BaseResponse):
            return resp

        representations = self.representations or {}

        mediatype = request.accept_mimetypes.best_match(representations, default=None)
        if mediatype in representations:
            data, code, headers = unpack(resp)
            resp = representations[mediatype](data, code, headers)
            resp.headers["Content-Type"] = mediatype
            return resp

        return resp


# class Configuration(ServiceResource):
#
#     @staticmethod
#     def selection_dialog():
#         return {
#             'title': 'Configuration Picker',
#             'label': 'Selection Component',
#             'uri': 'config/selection',
#             'hintWidth': '600px',
#             'hintHeight': '500px',
#             'resource_type': [JAZZ_CONFIG.Configuration],
#             'usages': [JAZZ_CONFIG.Configuration]
#         }
