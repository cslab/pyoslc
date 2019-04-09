from flask_restplus import Namespace

from webservice.api.oslc import api
from webservice.api.oslc.adapter.endpoints import ServiceProviderCatalog, ServiceProvider
from webservice.api.oslc.adapter.endpoints import Service, QueryCapability, CreationFactory

adapter_ns = Namespace(name='adapter', description='Python OSLC Adapter', path='/adapter')

adapter_ns.add_resource(ServiceProviderCatalog, '/catalog')
adapter_ns.add_resource(ServiceProvider, '/serviceprovider/<string:service_provider_id>')
adapter_ns.add_resource(Service, '/service/<string:service_id>')
adapter_ns.add_resource(QueryCapability, '/query/<string:query_capability_id>')
adapter_ns.add_resource(CreationFactory, '/creation/<string:creation_factory_id>')

api.add_namespace(adapter_ns)
