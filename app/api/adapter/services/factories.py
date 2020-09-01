from app.api.adapter.resources.resource_service import get_service_resources
from app.api.adapter.services.specification import ServiceResource
from pyoslc.resources.factories import ServiceProviderFactory, ConfigurationFactory


class ContactServiceProviderFactory(object):

    @classmethod
    def create_service_provider(cls, base_uri, title, description, publisher, parameters):
        classes = get_service_resources(ServiceResource)

        sp = ServiceProviderFactory.create_service_provider(base_uri, title, description,
                                                            publisher, classes, parameters)

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


class ContactConfigurationFactory(object):

    @classmethod
    def create_components(cls, base_uri, title, description, publisher, parameters):

        resource_attributes = {
            'title': 'Configuration Picker',
            'label': 'Selection Component',
            'uri': 'selection',
            'hint_width': '600px',
            'hint_height': '500px',
            'resource_type': ['http://jazz.net/ns/vvc#Configuration'],
            'usages': ['http://jazz.net/ns/vvc#Configuration']
        }

        component = ConfigurationFactory.create_component(base_uri, title, description,
                                                          publisher, resource_attributes, parameters)
        return component
