from flask import request

from pyoslc.resource import ServiceProviderCatalog, ServiceProvider, Service, QueryCapability, CreationFactory, \
    Publisher, OAuthConfiguration

base_url = 'http://localhost:5000/oslc'


creation_factory = CreationFactory(base_url + '/creation')
creation_factory.title = 'Creation title'
creation_factory.label = 'Creation factory label'

query_capability = QueryCapability(base_url + '/query')
query_capability.title = 'Query title'
query_capability.label = 'Query capability label'
query_capability.query_base = 'http://localhost:5000/oslc/rm/requirements'

service = Service(base_url + "/service")
service.title = 'Service title'
service.domain = 'http://open-services.net/ns/rm#'
service.add_creation_factory(creation_factory)
service.add_query_capability(query_capability)

publisher = Publisher(base_url + "/catalog/publisher")
publisher.title = "Contact Software Company"
publisher.label = "Contact Software"

oauth_configuration = OAuthConfiguration(base_url + "/oauth")
oauth_configuration.autorization_uri = base_url + "/authorization"

service_provider = ServiceProvider(base_url + "/serviceprovider")
service_provider.title = 'Service Provider title'
service_provider.description = 'Service Provider description'
service_provider.publisher = publisher
service_provider.add_service(service)
service_provider.details = base_url + 'serviceprovider/details'
service_provider.oauth_configuration = oauth_configuration

service_provider_catalog_2 = ServiceProviderCatalog(base_url + "/catalog/2")

service_provider_catalog = ServiceProviderCatalog(base_url + "/catalog")
service_provider_catalog.title = "Service Provider Catalog for Contact Software Application"
service_provider_catalog.description = "Catalog of services and resources for the applications"
service_provider_catalog.publisher = publisher
service_provider_catalog.add_service_provider(service_provider)
service_provider_catalog.add_service_provider_catalog(service_provider_catalog_2)
service_provider_catalog.oauth_configuration = oauth_configuration
