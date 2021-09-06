from xml.sax import SAXParseException

from rdflib import Graph
from six.moves.urllib.parse import urlparse
from werkzeug.exceptions import UnsupportedMediaType, BadRequest, NotImplemented, NotFound

from pyoslc_server import request

from pyoslc.resources.models import ResponseInfo, BaseResource, Compact, Preview
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
        if not(adapter in self.adapters):
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
            raise NotFound('The Service Provider with ID: {}, was not found.'.format(provider_id))

        provider.to_rdf(self.graph)
        return self.create_response(graph=self.graph)


class ResourceListOperation(OSLCResource):

    def get(self, provider_id):
        super(ResourceListOperation, self).get()

        # select = request.args.get('oslc.select', '')
        # where = request.args.get('oslc.where', '')

        endpoint_url = url_for('{}'.format(self.endpoint), provider_id=provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        rule = request.url_rule
        data = self.api.app.adapter_functions[rule.endpoint]('query_capability', **request.view_args)

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


class ResourceItemOperation(OSLCResource):

    def get(self, provider_id, resource_id):
        super(ResourceItemOperation, self).get()

        accept = request.headers['accept']

        endpoint_url = url_for('{}'.format(self.endpoint), provider_id=provider_id, resource_id=resource_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        rule = request.url_rule
        try:
            data = self.api.app.adapter_functions[rule.endpoint]('get_resource', **request.view_args)
            # requirement = get_requirement(base_url, requirement_id)
            resource = BaseResource()
            if data:
                resource.about = base_url
                attributes = [a['mapping'] for a in self.adapters if a['identifier'] == provider_id][0]

                r = Requirement()
                r.about = base_url
                # r.update()
                resource.update(data, attributes)
                resource.to_rdf_base(self.graph, base_url, attributes)

            if 'application/x-oslc-compact+xml' in accept or ', application/x-jazz-compact-rendering' in accept:
                compact = Compact(about=base_url)
                compact.title = resource.identifier if resource else 'REQ Not Found'
                compact.icon = url_for('oslc.static', filename='pyicon24.ico', _external=True)

                small_preview = Preview()
                small_preview.document = base_url + '/smallPreview'
                small_preview.hint_width = '45em'
                small_preview.hint_height = '10em'

                large_preview = Preview()
                large_preview.document = base_url + '/largePreview'
                large_preview.hint_width = '45em'
                large_preview.hint_height = '20em'

                compact.small_preview = small_preview
                compact.large_preview = large_preview

                compact.to_rdf(self.graph)

            return self.create_response(graph=self.graph,
                                        accept='application/x-oslc-compact+xml',
                                        rdf_format='pretty-xml',
                                        etag=True)
        except AssertionError as e:
            return NotImplemented(e)

    # def put(self, provider_id, resource_id):
    #     accept = request.headers.get('accept')
    #     if not (accept in ('application/rdf+xml', 'application/json', 'application/ld+json',
    #                        'application/xml', 'application/atom+xml')):
    #         raise UnsupportedMediaType
    #
    #     content = request.headers.get('content-type')
    #     if not (content in ('application/rdf+xml', 'application/json', 'application/ld+json',
    #                         'application/xml', 'application/atom+xml')):
    #         raise UnsupportedMediaType
    #
    #     endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
    #                            service_provider_id=service_provider_id, requirement_id=requirement_id)
    #     base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)
    #
    #     etag = request.headers.get(key='If-Match', default=None, type=str)
    #
    #     rq = CsvRequirementRepository('specs')
    #     r = rq.find(requirement_id)
    #     r.about = base_url
    #
    #     if not r:
    #         raise NotFound()
    #     # elif r.identifier != requirement_id:
    #     #     raise Conflict()
    #     elif not etag:
    #         raise BadRequest()
    #     else:
    #         dig = r.digestion()
    #         if dig != etag.strip("\""):
    #             raise PreconditionFailed()
    #
    #     g = Graph()
    #     try:
    #         data = g.parse(data=request.data, format='xml')
    #     except SAXParseException:
    #         raise NotAcceptable()
    #
    #     req = update_requirement(requirement_id, data)
    #     if isinstance(req, Requirement):
    #         req.to_rdf(self.graph, base_url, attributes)
    #         return self.create_response(self.graph)
    #     else:
    #         return make_response(req.description, req.code)

    # def delete(self, provider_id, resource_id):
    #     rq = CsvRequirementRepository('specs')
    #     r = rq.find(requirement_id)
    #
    #     if r:
    #         req = delete_requirement(requirement_id)
    #         if req:
    #             response = make_response('Resource deleted.', 200)
    #             # response.headers['Accept'] = 'application/rdf+xml'
    #             # response.headers['Content-Type'] = 'application/rdf+xml'
    #             # response.headers['OSLC-Core-Version'] = "2.0"
    #             return response
    #         else:
    #             return make_response(req.description, req.code)
    #     else:
    #         return make_response('The resource was not found.', 404)
