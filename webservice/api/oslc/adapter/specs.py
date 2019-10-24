class DataSpecsProjectA(object):

    domain = 'http://jazz.net/ns/iot#'

    @staticmethod
    def query_capability():
        return {
            'title': 'Query Capability Title',
            'label': 'Query Capability Label',
            'resource_shape': 'resourceShapes/deviceType',
            'resource_type': ['http://jazz.net/ns/iot#DeviceType'],
            'usages': []
        }

    @staticmethod
    def creation_factory():
        return {'title': 'Creation Factory',
                'label': 'Creation Factory Label',
                'resource_shape': ['resourceShapes/deviceType'],
                'resource_type': ['http://jazz.net/ns/iot#DeviceType'],
                'usages': []}

    @staticmethod
    def creation_dialog():
        return {
            'title': 'Creation Dialog',
            'label': 'Creation Dialog service',
            'uri': 'iotp/{id}/resources/creator',
            'hintWidth': '525px',
            'hintHeight': '325px',
            'resource_shape': 'resourceShapes/eventType',
            'resource_type': ['http://open-services.net/ns/cm#ChangeRequest',
                              'http://open-services.net/ns/am#Resource',
                              'http://open-services.net/ns/rm#Requirement'],
            'usages': ['http://open-services.net/ns/am#IoTPCreationDialog']
        }

    @staticmethod
    def selection_dialog():
        return {'title': 'Selection Dialog',
                'label': 'Selection Dialog Service',
                'uri': 'iotp/{id}/resources/selector',
                'hintWidth': '525px',
                'hintHeight': '325px',
                'resource_type': ['http://open-services.net/ns/cm#ChangeRequest',
                                  'http://open-services.net/ns/am#Resource',
                                  'http://open-services.net/ns/rm#Requirement'],
                'usages': ['http://open-services.net/ns/am#IoTPSelectionDialog']}