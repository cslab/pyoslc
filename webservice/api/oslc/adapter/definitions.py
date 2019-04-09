from flask import request

from pyoslc.resource import ServiceProviderCatalog, ServiceProvider, Service, QueryCapability, CreationFactory

base_url = 'http://localhost:5000/oslc/adapter'


creation_factory = CreationFactory(base_url + '/creation')
creation_factory.title = 'Creation title'
creation_factory.label = 'Creation factory label'

query_capability = QueryCapability(base_url + '/query')
query_capability.title = 'Query title'
query_capability.label = 'Query capability label'

service = Service(base_url + "/service")
service.title = 'Service title'
service.domain = 'http://open-services.net/ns/rm#'
service.add_creation_factory(creation_factory)
service.add_query_capability(query_capability)

service_provider = ServiceProvider(base_url + "/serviceprovider")
service_provider.title = 'Service Provider title'
service_provider.description = 'Service Provider description'
service_provider.add_service(service)

service_provider_catalog = ServiceProviderCatalog(base_url + "/catalog")
service_provider_catalog.title = "Catalog Title"
service_provider_catalog.add_domain({'jazz': 'http://jazz.net/xmlns/prod/jazz/process/1.0/'})
service_provider_catalog.add_service_provider(service_provider)
