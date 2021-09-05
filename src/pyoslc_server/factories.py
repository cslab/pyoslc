import inspect
from urlparse import urlparse

from pyoslc.resources.models import ServiceProvider, Service, QueryCapability, CreationFactory, Dialog
from .resource_service import get_service_resources
from .specification import ServiceResource


class ContactServiceProviderFactory(object):

    @classmethod
    def create_service_provider(cls, base_uri, title, description, publisher, parameters):
        classes = get_service_resources(parameters.get('id'), ServiceResource)

        sp = ServiceProviderFactory.create_service_provider(base_uri, title, description, publisher, classes, parameters)

        sp.add_detail(base_uri)

        prefix_definitions = list()
        # prefix_definitions.append(PrefixDefinition(prefix='dcterms', prefix_base=DCTERMS))
        # prefix_definitions.append(PrefixDefinition(prefix='oslc', prefix_base=OSLC))
        # prefix_definitions.append(PrefixDefinition(prefix='oslc_data', prefix_base=OSLCData))
        # prefix_definitions.append(PrefixDefinition(prefix='rdf', prefix_base=RDF))
        # prefix_definitions.append(PrefixDefinition(prefix='rdfs', prefix_base=RDFS))
        # prefix_definitions.append(PrefixDefinition(prefix='oslc_am', prefix_base=OSLC_AM))
        # prefix_definitions.append(PrefixDefinition(prefix='oslc_cm', prefix_base=OSLC_CM))
        # prefix_definitions.append(PrefixDefinition(prefix='oslc_rm', prefix_base=OSLC_RM))

        sp.prefix_definition = prefix_definitions

        return sp


class ServiceProviderFactory(object):

    @classmethod
    def create_service_provider(cls, base_uri, title, description, publisher, resource_classes, parameters):
        return cls.initialize(ServiceProvider(), base_uri, title, description, publisher, resource_classes, parameters)

    @classmethod
    def initialize(cls, service_provider, base_uri, title, description, publisher, resource_classes,
                   parameters):

        service_provider.title = title
        service_provider.description = description
        service_provider.publisher = publisher

        services = dict()

        for class_ in resource_classes:
            if class_.methods:

                service = services.get(class_.__name__)
                if not service:
                    assert class_.type, 'The OSLC Resource Type attribute is required in the {}'.format(class_.__name__)
                    assert class_.domain, 'The OSLC Domain attribute is required in the {}'.format(class_.__name__)
                    assert class_.service_path, 'The Service Path attribute is required in the {}'.format(class_.__name__)
                    service = Service(domain=class_.domain)
                    services[class_.domain] = service

                path = class_.service_path

                cls.handle_resource_class(base_uri, class_, service, parameters, path)

        for s in services.values():
            service_provider.add_service(s)

        return service_provider

    @classmethod
    def handle_resource_class(cls, base_uri, klass, service, parameters, path):

        for item in inspect.classify_class_attrs(klass):
            if item.kind.__contains__('method') and item.defining_class == klass and item.name != '__init__':

                if item.name == 'query_capability':
                    resource_attributes = {
                        'title': 'Query Capability',
                        'label': 'Query Capability',
                        'resource_shape': 'resourceShapes/requirement',
                        'resource_type': klass.type,
                        'usages': []
                    }
                    query_capability = cls.create_query_capability(base_uri, path, resource_attributes, parameters)
                    service.add_query_capability(query_capability)
                    # resource_shape = query_capability.resource_shape

                if item.name == 'creation_factory':
                    resource_attributes = {
                        'title': 'Creation Factory',
                        'label': 'Creation Factory',
                        'resource_shape': ['resourceShapes/requirement'],
                        'resource_type': klass.type,
                        'usages': []
                    }
                    creation_factory = cls.create_creation_factory(base_uri, resource_attributes, parameters)
                    service.add_creation_factory(creation_factory)
                    # resource_shape = creation_factory.resource_shape

                if item.name == 'selection_dialog':
                    resource_attributes = {
                        'title': 'Selection Dialog',
                        'label': 'Selection Dialog Service',
                        'uri': '{}/selector'.format(path),
                        'hint_width': '525px',
                        'hint_height': '325px',
                        'resource_type': klass.type,
                        'usages': ['http://open-services.net/ns/am#PyOSLCSelectionDialog']
                    }
                    dialog = cls.create_selection_dialog(base_uri, resource_attributes, parameters)
                    service.add_selection_dialog(dialog)

                if item.name == 'creation_dialog':
                    resource_attributes = {
                        'title': 'Creation Dialog',
                        'label': 'Creation Dialog service',
                        'uri': 'provider/{id}/resources/creator',
                        'hint_width': '525px',
                        'hint_height': '325px',
                        'resource_shape': 'resourceShapes/eventType',
                        'resource_type': klass.type,
                        'usages': ['http://open-services.net/ns/am#PyOSLCCreationDialog']
                    }
                    dialog = cls.create_creation_dialog(base_uri, resource_attributes, parameters)
                    service.add_creation_dialog(dialog)

        return True

    @classmethod
    def create_query_capability(cls, base_uri, path, attributes, parameters):

        title = attributes.get('title', 'OSLC Query Capability')
        label = attributes.get('label', 'Query Capability Service')
        resource_shape = attributes.get('resource_shape', '')
        resource_type = attributes.get('resource_type', list())
        usages = attributes.get('usages', list())

        base_path = base_uri + '/'
        class_path = path  # 'provider/{id}/resources'
        method_path = ''

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
    def create_creation_factory(cls, base_uri, attributes, parameters):
        class_path = 'provider/{id}/resources'
        method_path = 'requirement'
        creation_factory = cls.creation_factory(base_uri, attributes, parameters, class_path, method_path)
        return creation_factory

    @classmethod
    def creation_factory(cls, base_uri, attributes, parameters, class_path, method_path):

        title = attributes.get('title', 'OSLC Creation Factory')
        label = attributes.get('label', 'Creation Factory Service')
        resource_shape = attributes.get('resource_shape', list())
        resource_type = attributes.get('resource_type', list())
        usages = attributes.get('usages', list())

        base_path = base_uri + '/'

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
    def create_selection_dialog(cls, base_uri, attributes, parameters):
        return cls.create_dialog(base_uri, 'Selection', attributes, parameters)

    @classmethod
    def create_creation_dialog(cls, base_uri, attributes, parameters):
        return cls.create_dialog(base_uri, 'Creation', attributes, parameters)

    @classmethod
    def create_dialog(cls, base_uri, dialog_type, attributes, parameters):
        title = attributes.get('title', 'OSLC Dialog Resource Shape')
        label = attributes.get('label', 'OSLC Dialog for Service')
        dialog_uri = attributes.get('uri', None)
        hint_width = attributes.get('hint_width', '100px')
        hint_height = attributes.get('hint_height', '100px')
        resource_type = attributes.get('resource_type', list())
        usages = attributes.get('usages', list())

        if dialog_uri:
            uri = cls.resolve_path_parameter(base_uri, None, dialog_uri, parameters)
            uri = uri.replace('/catalog', '')
        else:
            uri = base_uri + 'generic/generic' + dialog_type + '.html'
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
