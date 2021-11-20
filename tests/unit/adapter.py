from pyoslc.vocabularies.rm import OSLC_RM
from pyoslc_server.specification import ServiceResourceAdapter


class BaseAdapter(ServiceResourceAdapter):

    def __init__(self, **kwargs):
        super(BaseAdapter, self).__init__(
            identifier='AdapterTest',
            title='RM Test Service',
            mapping=None,
            **kwargs
        )


class RMAdapter(BaseAdapter):

    def __init__(self, **kwargs):
        super(RMAdapter, self).__init__(**kwargs)
        self.types = [OSLC_RM.Requirement]

    domain = OSLC_RM
