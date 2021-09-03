from xml.sax import SAXParseException

from rdflib import Graph
from six.moves.urllib.parse import urlparse
from werkzeug.exceptions import UnsupportedMediaType, BadRequest

from pyoslc_server import request

from pyoslc.resources.models import ResponseInfo
from pyoslc.resources.domains.rm import Requirement

from .resource import OSLCResource
from .providers import ServiceProviderCatalogSingleton
from .helpers import url_for, make_response
from .wrappers import Response


class ServiceProviderCatalog(OSLCResource):

    def __init__(self, *args, **kwargs):
        super(ServiceProviderCatalog, self).__init__(*args, **kwargs)
        self.title = kwargs.get('title', None)
        self.description = kwargs.get('description', None)
        adapter = kwargs.get('adapter', None)
        if not adapter in self.adapters:
            self.adapters.append(adapter)

    def get(self):
        super(ServiceProviderCatalog, self).get()
        endpoint_url = url_for('{}'.format(request.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        catalog_url = urlparse(base_url).geturl()

        catalog = ServiceProviderCatalogSingleton.get_catalog(catalog_url, self.title, self.description, self.adapters)
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

        provider = ServiceProviderCatalogSingleton.get_provider(service_provider_url, provider_id,
                                                                adapters=self.adapters)

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

    def post(self, provider_id):
        accept = request.headers.get('accept')
        if not (accept in ('text/turtle', 'application/rdf+xml', 'application/json', 'application/ld+json',
                           'application/xml', 'application/atom+xml')):
            raise UnsupportedMediaType

        endpoint_url = url_for('{}'.format(self.endpoint), provider_id=provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        from apposlc.adapter import REQ_TO_RDF
        req = None
        if accept == 'application/json':
            # data = specification_parser.parse_args()
            pass
        else:
            try:
                data = Graph().parse(data=request.data, format='xml')
                req = Requirement()

                req.from_rdf(data, attributes=REQ_TO_RDF)
            except SAXParseException:
                raise BadRequest()

        if isinstance(req, Requirement):
            req.to_rdf(self.graph, base_url=base_url, attributes=REQ_TO_RDF)
            data = self.graph.serialize(format='pretty-xml')

            # Sending the response to the client
            response = Response(data.decode('utf-8') if not isinstance(data, str) else data, 201)
            response.headers['Content-Type'] = 'application/rdf+xml; charset=UTF-8'
            response.headers['OSLC-Core-Version'] = "2.0"
            response.headers['Location'] = base_url + '/' + req.identifier
            response.set_etag(req.digestion())
            # response.headers['Last-Modified'] = http_date(datetime.now())

            return response
        else:
            return make_response(req.description, req.code)
