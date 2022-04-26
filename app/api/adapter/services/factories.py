from pyoslc.resources.factories import ConfigurationFactory
from pyoslc.vocabularies.jazz import JAZZ_CONFIG


class ContactConfigurationFactory(object):
    @classmethod
    def create_components(cls, base_uri, title, description, publisher, parameters):

        resource_attributes = {
            "title": "Configuration Picker",
            "label": "Selection Component",
            "uri": "selection",
            "hint_width": "600px",
            "hint_height": "500px",
            "resource_type": [JAZZ_CONFIG.Configuration],
            "usages": [JAZZ_CONFIG.Configuration],
        }

        component = ConfigurationFactory.create_component(
            base_uri, title, description, publisher, resource_attributes, parameters
        )
        return component
