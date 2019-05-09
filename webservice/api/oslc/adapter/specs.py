class DataSpecsProjectA(object):

    domain = 'http://jazz.net/ns/iot#'

    @staticmethod
    def query_capability():
       return {
            'title': 'Query Capability Title',
            'label': 'Query Capability Label',
            'resource_shape': 'resourceShapes/eventType',
            'resource_type': ['http://jazz.net/ns/iot#EventType'],
            'usages': []
        }

    @staticmethod
    def dialog():
        return {
            'title': 'EventTypeQueryCapability',
            'label': 'Event Type Query Capability',
            'hint_width': '200',
            'resource_shape': 'resourceShapes/eventType',
            'resource_type': ['http://jazz.net/ns/iot#EventType'],
            'usages': []
        }

    @staticmethod
    def creation_factory():
        return {'title': 'Creation Factory'}


class DataSpecsProjectB(object):

    domain = 'http://jazz.net/ns/iot#'

    @staticmethod
    def query_capability():
        return {
            'title': 'Query Capability Title',
            'label': 'Query Capability Label',
            'resource_shape': 'resourceShapes/eventType',
            'resource_type': ['http://jazz.net/ns/iot#EventType'],
            'usages': []
        }

    @staticmethod
    def dialog():
        return {
            'title': 'EventTypeQueryCapability',
            'label': 'Event Type Query Capability',
            'resource_shape': 'resourceShapes/eventType',
            'resource_type': ['http://jazz.net/ns/iot#EventType'],
            'usages': []
        }

    @staticmethod
    def creation_factory():
        return {'title': 'Creation Factory'}
