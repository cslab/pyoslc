from flask_restplus import Namespace

from webservice.api.oslc import api
from webservice.api.oslc.adapter.endpoints import Catalog

adapter_ns = Namespace(name='adapter', description='Python OSLC Adapter', path='/adapter')

adapter_ns.add_resource(Catalog, '/')

api.add_namespace(adapter_ns)
