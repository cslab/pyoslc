import inspect
from urlparse import urlparse

from pyoslc.resource import ServiceProvider, Service, QueryCapability, CreationFactory, Dialog


class ServiceProviderFactory(object):

    @classmethod
    def create(cls, base_uri, generic_base_uri, title, description, publisher, resource_classes, parameters):
        return cls.initialize(ServiceProvider(), base_uri, generic_base_uri, title, description, publisher,
                              resource_classes, parameters)

    @classmethod
    def initialize(cls, service_provider, base_uri, generic_base_uri, title, description, publisher, resouce_classes,
                   parameters):

        # service_provider.title = title
        # service_provider.description = description
        service_provider.publisher = publisher

        services = dict()

        for class_ in resouce_classes:
            service = services.get(class_.domain)
            if not service:
                service = Service(about='http://baseurl/oslc/services/Project-1/service', domain=class_.domain)
                services[class_.domain] = service

            cls.handle_resource_class(base_uri, generic_base_uri, class_, service, parameters)

        for s in services.values():
            service_provider.add_service(s)

        return service_provider

    @classmethod
    def handle_resource_class(cls, base_uri, generic_base_uri, klass, service, parameters):

        for item in inspect.classify_class_attrs(klass):
            if item.kind.__contains__('method') and item.defining_class == klass:

                resource_shape = None
                if item.name is 'query_capability':
                    query_capability = cls.create_query_capability(base_uri, item.object, parameters)
                    service.add_query_capability(query_capability)
                    resource_shape = query_capability.resource_shape

                if item.name is 'creation_factory':
                    creation_factory = cls.create_creation_factory(base_uri, item.object, parameters)
                    service.add_creation_factory(creation_factory)
                    resource_shape = creation_factory.resource_shape

                if item.name is 'selection_dialog':
                    annotation = item.name
                    dialog = cls.create_selection_dialog(base_uri, generic_base_uri, item.object, annotation,
                                                         resource_shape, parameters)
                    service.add_selection_dialog(dialog)

                if item.name is 'creation_dialog':
                    annotation = item.name
                    dialog = cls.create_creation_dialog(base_uri, generic_base_uri, item.object, annotation,
                                                         resource_shape, parameters)
                    service.add_creation_dialog(dialog)

        return True

    @classmethod
    def create_query_capability(cls, base_uri, method, parameters):

        attributes = method.__func__()

        title = attributes.get('title', 'OSLC Query Capability')
        # label = attributes.get('label', 'Query Capability Service')
        label = None
        resource_shape = attributes.get('resource_shape', '')
        resource_type = attributes.get('resource_type', list())
        usages = attributes.get('usages', list())

        base_uri = base_uri.replace('localhost:5000', 'baseurl')
        base_uri = base_uri.replace('127.0.0.1:5000', 'baseurl')
        base_uri = base_uri.replace('0.0.0.0:5000', 'baseurl')

        base_path = base_uri + '/'
        class_path = 'project/{id}/resources'
        method_path = 'requirement'

        base_path = base_path.replace('/catalog', '')

        query = cls.resolve_path_parameter(base_path, class_path, method_path, parameters)

        query_capability = QueryCapability(about=query, title=title, query_base=query)
        if label:
            query_capability.label = label

        if resource_shape:
            resource_shape_url = urlparse(base_path + resource_shape)
            query_capability.resource_shape = resource_shape_url.geturl()

        for rt in resource_type:
            query_capability.add_resource_type(rt)

        for u in usages:
            query_capability.add_usage(u)

        return query_capability

    @classmethod
    def create_creation_factory(cls, base_uri, method, parameters):

        base_uri = base_uri.replace('localhost:5000', 'baseurl')
        base_uri = base_uri.replace('127.0.0.1:5000', 'baseurl')
        base_uri = base_uri.replace('0.0.0.0:5000', 'baseurl')

        class_path = 'project/{id}/resources'
        method_path = 'logic/rule'
        creation_factory = cls.creation_factory(base_uri, method, parameters, class_path, method_path)
        return creation_factory

    @classmethod
    def creation_factory(cls, base_uri, method, parameters, path, annotation):

        attributes = method.__func__()

        title = attributes.get('title', 'OSLC Creation Factory')
        label = attributes.get('label', 'Creation Factory Service')
        resource_shape = attributes.get('resource_shape', list())
        resource_type = attributes.get('resource_type', list())
        usages = attributes.get('usages', list())

        base_path = base_uri + '/'
        class_path = 'project/{id}/resources'
        method_path = 'requirement'

        creation = cls.resolve_path_parameter(base_path, class_path, method_path, parameters)
        creation = creation.replace('/catalog', '')

        creation_factory = CreationFactory(about=creation, title=title, creation=creation)

        if label:
            creation_factory.label = label

        for rs in resource_shape:
            resource_shape_url = urlparse(base_path + rs)
            creation_factory.add_resource_shape(resource_shape_url.geturl())

        for rt in resource_type:
            creation_factory.add_resource_type(rt)

        for u in usages:
            creation_factory.add_usage(u)

        return creation_factory

    @classmethod
    def create_selection_dialog(cls, base_uri, generic_base_uri, method, annotation, resource_shape, parameters):
        return cls.create_dialog(base_uri,
                                 generic_base_uri,
                                 'Selection',
                                 'query_base',
                                 method,
                                 annotation,
                                 resource_shape,
                                 parameters)

    @classmethod
    def create_creation_dialog(cls, base_uri, generic_base_uri, method, annotation, resource_shape, parameters):
        return cls.create_dialog(base_uri,
                                 generic_base_uri,
                                 'Creation',
                                 'creation',
                                 method,
                                 annotation,
                                 resource_shape,
                                 parameters)

    @classmethod
    def create_dialog(cls, base_uri, generic_base_uri, dialog_type, parameter_name, method, annotation, resource_shape,
                      parameters):
        attributes = method.__func__()

        title = attributes.get('title', 'OSLC Dialog Resource Shape')
        label = attributes.get('label', 'OSLC Dialog for Service')
        dialog_uri = attributes.get('uri', None)
        hint_width = attributes.get('hint_width', 100)
        hint_height = attributes.get('hint_height', 100)
        resource_type = attributes.get('resource_type', list())
        usages = attributes.get('usages', list())

        uri = ''
        class_method = 'project/{id}/resources'

        if dialog_uri:
            uri = cls.resolve_path_parameter(base_uri, None, dialog_uri, parameters)
        else:
            uri = generic_base_uri + 'generic/generic' + dialog_type + '.html'
            # Continue implementing generic dialog selector

        dialog = Dialog(title=title, dialog=uri)

        if label:
            dialog.label = label

        if hint_width:
            dialog.hint_width = hint_width

        if hint_height:
            dialog.hint_height = hint_height

        for rt in resource_type:
            dialog.add_resource_type(rt)

        for u in usages:
            dialog.add_usage(u)

        return dialog

    @classmethod
    def resolve_path_parameter(cls, base_path, class_path, method_path, parameters):

        base_path = base_path.rstrip('/')

        if class_path:
            base_path += '/' + class_path

        if method_path:
            base_path += '/' + method_path

        uri = urlparse(base_path.format(**parameters))

        return uri.geturl()
