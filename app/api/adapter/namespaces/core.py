import logging
from datetime import datetime

from pyoslc_server.providers import ServiceProviderCatalogSingleton
from pyoslc_server.resource import OSLCResource
from six.moves.urllib.parse import urlparse
from xml.sax import SAXParseException

from flask import request, make_response, url_for, render_template
from flask_restx import Namespace
from rdflib import Graph
from rdflib.plugin import register
from rdflib.serializer import Serializer
from werkzeug.exceptions import UnsupportedMediaType, NotAcceptable, PreconditionFailed, NotFound, BadRequest
from werkzeug.http import http_date

from app.api.adapter import api
from app.api.adapter.namespaces.business import get_requirement_list, get_requirement, attributes, create_requirement, \
    update_requirement, delete_requirement
from app.api.adapter.namespaces.rm.csv_requirement_repository import CsvRequirementRepository
from app.api.adapter.namespaces.rm.parsers import specification_parser
from app.api.adapter.resources.resource_service import config_service_resource
from app.api.adapter.services.providers import RootServiceSingleton, PublisherSingleton
from app.api.adapter.services.specification import ServiceResource
from pyoslc.resources.domains.rm import Requirement
from pyoslc.resources.models import ResponseInfo, Compact, Preview

logger = logging.getLogger(__name__)

adapter_ns = Namespace(name='adapter', description='Python OSLC Adapter', path='/services',)

register(
    'rootservices-xml', Serializer,
    'pyoslc.serializers.jazzxml', 'JazzRootServiceSerializer'
)

config_service_resource(
    'specification', ServiceResource,
    'app.api.adapter.services.specification', 'Specification',
)


@adapter_ns.route('/catalog')
@api.representation('application/rdf+xml')
@api.representation('application/json-ld')
@api.representation('text/turtle')
class ServiceProviderCatalog(OSLCResource):

    def __init__(self, *args, **kwargs):
        super(ServiceProviderCatalog, self).__init__(*args, **kwargs)

    def get(self):
        super(ServiceProviderCatalog, self).get()
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        catalog_url = urlparse(base_url).geturl()

        catalog = ServiceProviderCatalogSingleton.get_catalog(catalog_url)
        catalog.to_rdf(self.graph)

        return self.create_response(graph=self.graph)


@adapter_ns.route('/provider/<service_provider_id>')
@api.representation('application/rdf+xml')
@api.representation('application/json-ld')
@api.representation('text/turtle')
class ServiceProvider(OSLCResource):

    def __init__(self, *args, **kwargs):
        super(ServiceProvider, self).__init__(*args, **kwargs)

    def get(self, service_provider_id):
        super(ServiceProvider, self).get()
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        service_provider_url = urlparse(base_url).geturl()

        provider = ServiceProviderCatalogSingleton.get_provider(service_provider_url, service_provider_id)

        if not provider:
            return make_response('No resources with ID {}'.format(service_provider_id), 404)

        provider.to_rdf(self.graph)
        return self.create_response(graph=self.graph)


@adapter_ns.route('/provider/<service_provider_id>/resources/requirement')
@api.representation('application/rdf+xml')
@api.representation('application/json-ld')
@api.representation('text/turtle')
class ResourceOperation(OSLCResource):

    def get(self, service_provider_id):
        super(ResourceOperation, self).get()

        select = request.args.get('oslc.select', '')
        where = request.args.get('oslc.where', '')

        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        data = get_requirement_list(base_url, select, where)
        if len(data) == 0:
            return make_response('No resources form provider with ID {}'.format(service_provider_id), 404)

        response_info = ResponseInfo(base_url)
        response_info.total_count = len(data)
        response_info.title = 'Query Results for Requirements'

        response_info.members = data
        response_info.to_rdf(self.graph)

        return self.create_response(graph=self.graph)

    # @adapter_ns.expect(specification)
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


@adapter_ns.route('/provider/<service_provider_id>/resources/requirement/<requirement_id>')
@api.representation('application/rdf+xml')
@api.representation('application/json-ld')
@api.representation('text/turtle')
class ResourcePreview(OSLCResource):

    def get(self, service_provider_id, requirement_id):
        super(ResourcePreview, self).get()

        accept = request.headers['accept']

        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id, requirement_id=requirement_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        requirement = get_requirement(base_url, requirement_id)
        if requirement:
            requirement.about = base_url
            requirement.to_rdf(self.graph, base_url, attributes)

        if 'application/x-oslc-compact+xml' in accept or ', application/x-jazz-compact-rendering' in accept:
            compact = Compact(about=base_url)
            compact.title = requirement.identifier if requirement else 'REQ Not Found'
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

    def put(self, service_provider_id, requirement_id):
        accept = request.headers.get('accept')
        if not (accept in ('application/rdf+xml', 'application/json', 'application/ld+json',
                           'application/xml', 'application/atom+xml')):
            raise UnsupportedMediaType

        content = request.headers.get('content-type')
        if not (content in ('application/rdf+xml', 'application/json', 'application/ld+json',
                            'application/xml', 'application/atom+xml')):
            raise UnsupportedMediaType

        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id, requirement_id=requirement_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        etag = request.headers.get(key='If-Match', default=None, type=str)

        rq = CsvRequirementRepository('specs')
        r = rq.find(requirement_id)
        r.about = base_url

        if not r:
            raise NotFound()
        # elif r.identifier != requirement_id:
        #     raise Conflict()
        elif not etag:
            raise BadRequest()
        else:
            dig = r.digestion()
            if dig != etag.strip("\""):
                raise PreconditionFailed()

        g = Graph()
        try:
            data = g.parse(data=request.data, format='xml')
        except SAXParseException:
            raise NotAcceptable()

        req = update_requirement(requirement_id, data)
        if isinstance(req, Requirement):
            req.to_rdf(self.graph, base_url, attributes)
            return self.create_response(self.graph)
        else:
            return make_response(req.description, req.code)

    def delete(self, service_provider_id, requirement_id):
        rq = CsvRequirementRepository('specs')
        r = rq.find(requirement_id)

        if r:
            req = delete_requirement(requirement_id)
            if req:
                response = make_response('Resource deleted.', 200)
                # response.headers['Accept'] = 'application/rdf+xml'
                # response.headers['Content-Type'] = 'application/rdf+xml'
                # response.headers['OSLC-Core-Version'] = "2.0"
                return response
            else:
                return make_response(req.description, req.code)
        else:
            return make_response('The resource was not found.', 404)


@adapter_ns.route('/provider/<service_provider_id>/resources/requirement/<requirement_id>/<preview_type>')
class ResourcePreviewSmallLarge(OSLCResource):

    def get(self, service_provider_id, requirement_id, preview_type):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id, requirement_id=requirement_id,
                               preview_type=preview_type)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        requirement = get_requirement(base_url, requirement_id)

        template = "dialogs/"
        if preview_type == 'smallPreview':
            template += "smallpreview.html"

        if preview_type == 'largePreview':
            template += "/largepreview.html"

        response = make_response(render_template(template, title='small', requirement=requirement))

        response.headers['Content-Type'] = 'text/html;charset=UTF-8'
        response.headers['OSLC-Core-Version'] = "2.0"

        return response


@adapter_ns.route('/rootservices')
class RootServices(OSLCResource):

    def get(self):

        """
        Generate Rootservices response
        :return:
        """
        super(RootServices, self).get()

        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        rootservices_url = urlparse(base_url).geturl()

        root_services = RootServiceSingleton.get_root_service(rootservices_url)
        root_services.about = request.base_url
        publisher_url = rootservices_url.replace('rootservices', 'publisher')
        root_services.publisher = PublisherSingleton.get_publisher(publisher_url)
        root_services.to_rdf(self.graph)

        return self.create_response(graph=self.graph, rdf_format='rootservices-xml')


@adapter_ns.route('/config')
class ConfigurationCatalog(OSLCResource):

    def get(self):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        catalog_url = urlparse(base_url).geturl()

        response = make_response(render_template('pyoslc_oauth/configuration.html',
                                                 about=catalog_url,
                                                 components=catalog_url + '/components'))

        response.headers['max-age'] = '0'
        response.headers['pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Content-Length'] = len(response.data)
        response.headers['Content-Type'] = 'application/rdf+xml;charset=UTF-8'
        response.headers['OSLC-Core-Version'] = "2.0"

        return response


@adapter_ns.route('/config/components')
class ConfigurationComponent(OSLCResource):

    def get(self):
        super(ConfigurationComponent, self).get()
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        components_url = urlparse(base_url).geturl()

        response = make_response(render_template('pyoslc_oauth/components.html',
                                                 about=components_url,
                                                 dialog=components_url.replace('components', 'selection')))

        response.headers['max-age'] = '0'
        response.headers['pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Content-Length'] = len(response.data)
        response.headers['Content-Type'] = 'application/rdf+xml;charset=UTF-8'
        response.headers['OSLC-Core-Version'] = "2.0"

        return response


@adapter_ns.route('/config/publisher')
class ConfigurationPublisher(OSLCResource):

    def get(self):
        super(ConfigurationPublisher, self).get()
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        components_url = urlparse(base_url).geturl()

        response = make_response(render_template('pyoslc_oauth/publisher.html', about=components_url))

        response.headers['max-age'] = '0'
        response.headers['pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Content-Length'] = len(response.data)
        response.headers['Content-Type'] = 'application/rdf+xml;charset=UTF-8'
        response.headers['OSLC-Core-Version'] = "2.0"

        return response


@adapter_ns.route('/config/selection')
class ConfigurationSelection(OSLCResource):

    def get(self):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        components_url = urlparse(base_url).geturl()

        stream = request.args.get('stream')
        if stream:

            result = [
                {
                    'oslc:label': 'PyOSLC Stream 1',
                    'rdf:resource': url_for('oslc.adapter_configuration_stream', stream_id=1, _external=True),
                    'rdf:type': 'http://open-services.net/ns/config#Stream'

                },
                {
                    'oslc:label': 'PyOSLC Stream 2',
                    'rdf:resource': url_for('oslc.adapter_configuration_stream', stream_id=2, _external=True),
                    'rdf:type': 'http://open-services.net/ns/config#Stream'
                }
            ]

            return {"oslc:results": result}, 200

        response = make_response(render_template('pyoslc_oauth/selection.xhtml',
                                                 selection_uri=components_url.replace('components', 'selection')))

        response.headers['max-age'] = '0'
        response.headers['pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Content-Length'] = len(response.data)
        response.headers['Content-Type'] = 'application/rdf+xml;charset=UTF-8'
        response.headers['OSLC-Core-Version'] = "2.0"

        return response


@adapter_ns.route('/config/stream/<int:stream_id>')
class ConfigurationStream(OSLCResource):

    def get(self, stream_id):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint), stream_id=stream_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        stream_url = urlparse(base_url).geturl()

        catalog_url = url_for('oslc.adapter_service_provider_catalog', _external=True)
        service_provider_url = url_for('oslc.adapter_service_provider', service_provider_id='Project-1', _external=True)

        response = make_response(render_template('pyoslc_oauth/stream.html',
                                                 stream_url=stream_url,
                                                 selection_url=url_for('oslc.adapter_configuration_selection',
                                                                       _external=True),
                                                 stream_id=stream_id,
                                                 project_area=catalog_url,
                                                 service_provider_url=service_provider_url,
                                                 selection_uri=stream_url.replace('components', 'selection')))

        response.headers['max-age'] = '0'
        response.headers['pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Content-Length'] = len(response.data)
        response.headers['Content-Type'] = 'application/rdf+xml;charset=UTF-8'
        response.headers['OSLC-Core-Version'] = "2.0"

        return response


@adapter_ns.route('/scr')
class Source(OSLCResource):

    def get(self):
        response = make_response(render_template('pyoslc_oauth/scr.html'))
        return response
