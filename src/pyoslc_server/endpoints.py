from six.moves.urllib.parse import urlparse

from pyoslc_server import request

from .resource import OSLCResource
from .providers import ServiceProviderCatalogSingleton
from .helpers import url_for, make_response


class ServiceProviderCatalog(OSLCResource):

    title = ''
    description = ''
    providers = dict()

    def __init__(self, *args, **kwargs):
        super(ServiceProviderCatalog, self).__init__(*args, **kwargs)
        self.title = kwargs.get('title', None)
        self.description = kwargs.get('description', None)
        self.providers = kwargs.get('providers', None)

    def get(self):
        super(ServiceProviderCatalog, self).get()
        endpoint_url = url_for('{}'.format(request.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        catalog_url = urlparse(base_url).geturl()

        catalog = ServiceProviderCatalogSingleton.get_catalog(catalog_url, self.title, self.description, self.providers)
        catalog.to_rdf(self.graph)

        return self.create_response(graph=self.graph)


class ServiceProvider(OSLCResource):

    def __init__(self, *args, **kwargs):
        super(ServiceProvider, self).__init__(*args, **kwargs)
        self.title = kwargs.get('title', None)
        self.description = kwargs.get('description', None)
        self.providers = kwargs.get('providers', None)

    def get(self, provider_id):
        super(ServiceProvider, self).get()
        endpoint_url = url_for('{}'.format(self.endpoint), provider_id=provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        service_provider_url = urlparse(base_url).geturl()

        provider = ServiceProviderCatalogSingleton.get_provider(service_provider_url, provider_id, providers=self.providers)

        if not provider:
            return make_response('No resources with ID {}'.format(provider_id), 404)

        provider.to_rdf(self.graph)
        return self.create_response(graph=self.graph)


class ResourceOperation(OSLCResource):

    def get(self, provider_id):
        super(ResourceOperation, self).get()

        select = request.args.get('oslc.select', '')
        where = request.args.get('oslc.where', '')

        endpoint_url = url_for('{}'.format(self.endpoint), provider_id=provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        rule = request.url_rule
        data = self.api.app.adapter_functions[rule.endpoint+'adap'](**request.view_args)

        # data = get_requirement_list(base_url, select, where)
        if len(data) == 0:
            return make_response('No resources form provider with ID {}'.format(provider_id), 404)

        response_info = ResponseInfo(base_url)
        response_info.total_count = len(data)
        response_info.title = 'Query Results for Requirements'

        response_info.members = data
        response_info.to_rdf(self.graph)

        return self.create_response(graph=self.graph)

    def post(self, service_provider_id):
        accept = request.headers.get('accept')
        if not (accept in ('application/rdf+xml', 'application/json', 'application/ld+json',
                           'application/xml', 'application/atom+xml')):
            raise UnsupportedMediaType

        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        if accept == 'application/json':
            data = specification_parser.parse_args()
        else:
            try:
                data = Graph().parse(data=request.data, format='xml')
            except SAXParseException:
                raise BadRequest()

        req = create_requirement(data)
        if isinstance(req, Requirement):
            req.to_rdf(self.graph, base_url=base_url, attributes=attributes)
            data = self.graph.serialize(format='pretty-xml')

            # Sending the response to the client
            response = make_response(data.decode('utf-8') if not isinstance(data, str) else data, 201)
            response.headers['Content-Type'] = 'application/rdf+xml; charset=UTF-8'
            response.headers['OSLC-Core-Version'] = "2.0"
            response.headers['Location'] = base_url + '/' + req.identifier
            response.set_etag(req.digestion())
            response.headers['Last-Modified'] = http_date(datetime.now())

            return response
        else:
            return make_response(req.description, req.code)

