from pyoslc.vocabularies.jazz import JAZZ_CONFIG

method_funcs = frozenset(['creation_factory',
                          'query_capability',
                          'creation_dialog',
                          'selection_dialog'])


class Provider(object):
    methods = None

    provide_automatic_options = None

    decorators = ()

    def generate(self):
        raise NotImplementedError()

    @classmethod
    def as_provider(cls, name, *class_args, **class_kwargs):

        def provider(*args, **kwargs):
            self = provider.provider_class(*class_args, **class_kwargs)
            return self.generate(*args, **kwargs)

        if cls.decorators:
            provider.__name__ = name
            provider.__module__ = cls.__module__
            for decorator in cls.decorators:
                provider = decorator(provider)

        provider.provider_class = cls
        provider.__name__ = name
        provider.__doc__ = cls.__doc__
        provider.__module__ = cls.__module__
        provider.methods = cls.methods
        provider.provide_automatic_options = cls.provide_automatic_options
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


class ServiceResource(ProviderResource, Provider):

    def generate(self, *args, **kwargs):
        method = getattr(self, "", None)

        if method is None:
            method = getattr(self, 'query_capability', None)

        assert method is not None, 'Unimplemented method %r' % method
        return method(*args, **kwargs)


class Specification(ServiceResource):

    domain = 'http://open-services.net/ns/rm#'
    service_path = 'provider/{id}/resources'

    @staticmethod
    def query_capability():
        return {
            'title': 'Query Capability',
            'label': 'Query Capability',
            'resource_shape': 'resourceShapes/requirement',
            'resource_type': ['http://open-services.net/ns/rm#Requirement'],
            'usages': []
        }

    @staticmethod
    def creation_factory():
        return {
            'title': 'Creation Factory',
            'label': 'Creation Factory',
            'resource_shape': ['resourceShapes/requirement'],
            'resource_type': ['http://open-services.net/ns/rm#Requirement'],
            'usages': []
        }

    @staticmethod
    def selection_dialog():
        return {
            'title': 'Selection Dialog',
            'label': 'Selection Dialog Service',
            'uri': 'provider/{id}/resources/selector',
            'hint_width': '525px',
            'hint_height': '325px',
            'resource_type': ['http://open-services.net/ns/cm#ChangeRequest',
                              'http://open-services.net/ns/am#Resource',
                              'http://open-services.net/ns/rm#Requirement'],
            'usages': ['http://open-services.net/ns/am#PyOSLCSelectionDialog']
        }

    @staticmethod
    def creation_dialog():
        return {
            'title': 'Creation Dialog',
            'label': 'Creation Dialog service',
            'uri': 'provider/{id}/resources/creator',
            'hint_width': '525px',
            'hint_height': '325px',
            'resource_shape': 'resourceShapes/eventType',
            'resource_type': ['http://open-services.net/ns/cm#ChangeRequest',
                              'http://open-services.net/ns/am#Resource',
                              'http://open-services.net/ns/rm#Requirement'],
            'usages': ['http://open-services.net/ns/am#PyOSLCCreationDialog']
        }


class Configuration(ServiceResource):

    @staticmethod
    def selection_dialog():
        return {
            'title': 'Configuration Picker',
            'label': 'Selection Component',
            'uri': 'config/selection',
            'hintWidth': '600px',
            'hintHeight': '500px',
            'resource_type': [JAZZ_CONFIG.Configuration],
            'usages': [JAZZ_CONFIG.Configuration]
        }
