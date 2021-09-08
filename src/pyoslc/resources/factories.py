from pyoslc.resources.models import ServiceProvider, Service
from pyoslc.vocabularies.config import OSLC_CONFIG
from pyoslc_server.factories import ServiceProviderFactory


class ConfigurationFactory(object):

    @classmethod
    def create_component(cls, base_uri, title, description, publisher, attributes, parameters):
        component = ServiceProvider()
        component.title = title
        component.description = description
        component.publisher = publisher

        items = dict()
        item = Service(domain=OSLC_CONFIG.uri)

        items[OSLC_CONFIG.uri] = item

        dialog = ServiceProviderFactory.create_selection_dialog(base_uri, attributes, parameters)
        item.add_selection_dialog(dialog)

        for s in items.values():
            component.add_service(s)

        return component
