from app.api.adapter.services.specification import Specification


class CSVImplementation(object):

    @classmethod
    def get_service_provider_info(cls):
        service_providers = [{
            'id': 'Project-1',
            'name': 'PyOSLC Service Provider for Project 1',
            'class': Specification
        }]

        return service_providers

    @classmethod
    def get_configuration_info(cls):
        components = [{
            'id': 'Component-1',
            'name': 'PyOSLC Configuration Component'
        }]

        return components
