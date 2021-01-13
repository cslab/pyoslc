import csv
import os
import shutil
from datetime import datetime
from tempfile import NamedTemporaryFile
from six.moves.urllib.parse import urlparse
from xml.sax import SAXParseException

from flask import request, make_response, url_for, render_template
from flask_restx import Namespace, Resource
from rdflib import Graph, RDF, RDFS, BNode
from rdflib.namespace import DCTERMS
from rdflib.plugin import register
from rdflib.serializer import Serializer
from werkzeug.exceptions import UnsupportedMediaType, NotAcceptable, PreconditionFailed, NotFound, BadRequest
from werkzeug.http import http_date

from app.api.adapter.exceptions import NotModified
from app.api.adapter.namespaces.business import get_requirement_list, get_requirement, attributes
from app.api.adapter.namespaces.rm.csv_requirement_repository import CsvRequirementRepository
from app.api.adapter.namespaces.rm.models import specification
from app.api.adapter.namespaces.rm.parsers import specification_parser
from app.api.adapter.resources.resource_service import config_service_resource
from app.api.adapter.services.providers import ServiceProviderCatalogSingleton, RootServiceSingleton, PublisherSingleton
from app.api.adapter.services.specification import ServiceResource
from pyoslc.resources.domains.rm import Requirement
from pyoslc.resources.models import ResponseInfo, Compact, Preview
from pyoslc.vocabularies.core import OSLC
from pyoslc.vocabularies.jazz import JAZZ_PROCESS

adapter_ns = Namespace(name='adapter', description='Python OSLC Adapter', path='/services',)

register(
    'rootservices-xml', Serializer,
    'pyoslc.serializers.jazzxml', 'JazzRootServiceSerializer'
)

config_service_resource(
    'specification', ServiceResource,
    'app.api.adapter.services.specification', 'Specification',
)


class OslcResource(Resource):

    def __init__(self, *args, **kwargs):
        super(OslcResource, self).__init__(*args, **kwargs)

        self.graph = kwargs.get('graph', Graph())
        self.graph.bind('oslc', OSLC)
        self.graph.bind('rdf', RDF)
        self.graph.bind('rdfs', RDFS)
        self.graph.bind('dcterms', DCTERMS)
        self.graph.bind('j.0', JAZZ_PROCESS)

    def get(self, *args, **kwargs):
        accept = request.headers.get('accept')
        if not (accept in ('application/rdf+xml', 'application/json', 'application/ld+json',
                           'application/xml', 'application/atom+xml', )):
            raise UnsupportedMediaType

    @staticmethod
    def create_response(graph, accept=None, content=None, rdf_format=None, etag=False):

        # Getting the content-type for checking the
        # response we will use to serialize the RDF response.
        accept = accept if accept is not None else request.headers.get('accept', 'application/rdf+xml')
        content = content if content is not None else request.headers.get('content-type', accept)
        if content.__contains__('x-www-form-urlencoded'):
            content = accept

        rdf_format = accept if rdf_format is None else rdf_format

        if accept in ('application/json-ld', 'application/ld+json', 'application/json', '*/*'):
            # If the content-type is any kind of json,
            # we will use the json-ld format for the response.
            rdf_format = 'json-ld'

        # if rdf_format in 'config-xml':
        #     rdf_format = 'config-xml'
        # else:
        #     rdf_format = 'pretty-xml'

        if rdf_format in ('application/xml', 'application/rdf+xml'):
            rdf_format = 'pretty-xml'

        if rdf_format.__contains__('rootservices-xml') and (not accept.__contains__('xml')):
            rdf_format = accept

        if rdf_format == 'application/atom+xml':
            rdf_format = 'pretty-xml'

        if rdf_format in ('application/xml, application/x-oslc-cm-service-description+xml'):
            rdf_format = 'pretty-xml'
            content = 'application/rdf+xml'

        data = graph.serialize(format=rdf_format)

        # Sending the response to the client
        response = make_response(data.decode('utf-8'), 200)
        response.headers['Accept'] = accept
        response.headers['Content-Type'] = content
        response.headers['OSLC-Core-Version'] = "2.0"

        if etag:
            response.add_etag()

        return response


@adapter_ns.route('/catalog')
class ServiceProviderCatalog(OslcResource):

    def __init__(self, *args, **kwargs):
        super(ServiceProviderCatalog, self).__init__(*args, **kwargs)

    def get(self):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        catalog_url = urlparse(base_url).geturl()

        catalog = ServiceProviderCatalogSingleton.get_catalog(catalog_url)
        catalog.to_rdf(self.graph)

        return self.create_response(graph=self.graph)


@adapter_ns.route('/provider/<service_provider_id>')
class ServiceProvider(OslcResource):

    def __init__(self, *args, **kwargs):
        super(ServiceProvider, self).__init__(*args, **kwargs)

    def get(self, service_provider_id):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        service_provider_url = urlparse(base_url).geturl()

        provider = ServiceProviderCatalogSingleton.get_provider(service_provider_url, service_provider_id)
        provider.to_rdf(self.graph)
        return self.create_response(graph=self.graph)


@adapter_ns.route('/provider/<service_provider_id>/resources/requirement')
class ResourceOperation(OslcResource):

    def get(self, service_provider_id):
        super(ResourceOperation, self).get()

        select = request.args.get('oslc.select', '')
        where = request.args.get('oslc.where', '')

        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        data = get_requirement_list(base_url, select, where)
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

        req = Requirement()

        if accept == 'application/json':
            data = specification_parser.parse_args()
            req.from_json(data, attributes)
        else:

            g = Graph()
            try:
                g.parse(data=request.data, format='xml')
            except SAXParseException:
                raise BadRequest()

            req.from_rdf(g, attributes=attributes)

        req.identifier = BNode().title()
        req.about = base_url + '/' + req.identifier

        data = req.to_mapped_object(attributes)

        if data:
            path = 'examples/specifications.csv'

            tempfile = NamedTemporaryFile(mode='w', delete=False)

            with open(path, 'r') as f:
                reader = csv.DictReader(f, delimiter=';')
                field_names = reader.fieldnames

            with open(path, 'r') as csvfile, tempfile:
                reader = csv.DictReader(csvfile, fieldnames=field_names, delimiter=';')
                writer = csv.DictWriter(tempfile, fieldnames=field_names, delimiter=';')
                exist = False
                for row in reader:
                    if row['Specification_id'] == data['Specification_id']:
                        exist = True
                    writer.writerow(row)

                if not exist:
                    writer.writerow(data)

            shutil.move(tempfile.name, path)

            if exist:
                raise NotModified()

        else:
            raise NotFound()

        req.to_rdf(self.graph, base_url=base_url, attributes=attributes)
        data = self.graph.serialize(format='pretty-xml')

        # Sending the response to the client
        response = make_response(data.decode('utf-8'), 201)
        response.headers['Content-Type'] = 'application/rdf+xml; charset=UTF-8'
        response.headers['OSLC-Core-Version'] = "2.0"
        response.headers['Location'] = base_url + '/' + req.identifier
        response.set_etag(req.digestion())
        response.headers['Last-Modified'] = http_date(datetime.now())

        return response


@adapter_ns.route('/provider/<service_provider_id>/resources/requirement/<requirement_id>')
class ResourcePreview(OslcResource):

    def get(self, service_provider_id, requirement_id):
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

    @adapter_ns.expect(specification)
    def post(self, service_provider_id):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        data = specification_parser.parse_args()

        req = Requirement()
        req.from_json(data, attributes)
        data = req.to_mapped_object(attributes)

        if data:
            path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')

            tempfile = NamedTemporaryFile(mode='w', delete=False)

            with open(path, 'rb') as f:
                reader = csv.DictReader(f, delimiter=';')
                field_names = reader.fieldnames

            with open(path, 'r') as csvfile, tempfile:
                reader = csv.DictReader(csvfile, fieldnames=field_names, delimiter=';')
                writer = csv.DictWriter(tempfile, fieldnames=field_names, delimiter=';')
                exist = False
                for row in reader:
                    if row['Specification_id'] == data['Specification_id']:
                        exist = True
                    writer.writerow(row)

                if not exist:
                    writer.writerow(data)

            shutil.move(tempfile.name, path)

            if exist:
                response_object = {
                    'status': 'fail',
                    'message': 'Not Modified'
                }
                return response_object, 304

        else:
            response_object = {
                'status': 'fail',
                'message': 'Not Found'
            }
            return response_object, 400

        response = make_response('', 201)
        response.headers['Content-Type'] = 'application/rdf+xml; charset=UTF-8'
        response.headers['OSLC-Core-Version'] = "2.0"
        response.headers['Location'] = base_url + '/' + req.identifier

        return response

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
            g.parse(data=request.data, format='xml')
        except SAXParseException:
            raise NotAcceptable()

        req = Requirement()
        req.from_rdf(g, attributes=attributes)
        req.identifier = requirement_id
        req.about = base_url

        data = req.to_mapped_object(attributes)

        if data:
            path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')

            tempfile = NamedTemporaryFile(mode='w', delete=False)

            with open(path, 'rb') as f:
                reader = csv.DictReader(f, delimiter=';')
                field_names = reader.fieldnames

            modified = False
            with open(path, 'r') as csvfile, tempfile:
                reader = csv.DictReader(csvfile, fieldnames=field_names, delimiter=';')
                writer = csv.DictWriter(tempfile, fieldnames=field_names, delimiter=';')
                for row in reader:
                    if row['Specification_id'] == str(requirement_id):
                        rq = Requirement()
                        rq.from_json(data, attributes=attributes)
                        row = rq.to_mapped_object(attributes=attributes)
                        row['Specification_id'] = requirement_id
                        modified = True
                    writer.writerow(row)

            shutil.move(tempfile.name, path)

            if not modified:
                raise NotModified()

        req.to_rdf(self.graph, base_url, attributes)

        return self.create_response(self.graph)

    def delete(self, service_provider_id, requirement_id):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id, requirement_id=requirement_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        rq = CsvRequirementRepository('specs')
        r = rq.find(requirement_id)

        if r:
            r.about = base_url

            path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')

            tempfile = NamedTemporaryFile(mode='w', delete=False)

            with open(path, 'rb') as f:
                reader = csv.DictReader(f, delimiter=';')
                field_names = reader.fieldnames

            modified = False
            with open(path, 'r') as csvfile, tempfile:
                reader = csv.DictReader(csvfile, fieldnames=field_names, delimiter=';')
                writer = csv.DictWriter(tempfile, fieldnames=field_names, delimiter=';')
                for row in reader:
                    if row['Specification_id'] != str(requirement_id):
                        writer.writerow(row)
                    else:
                        modified = True

            shutil.move(tempfile.name, path)

            if not modified:
                raise NotModified()

            r.to_rdf(self.graph, base_url, attributes=attributes)

            return self.create_response(self.graph)

        else:
            raise NotFound()


@adapter_ns.route('/provider/<service_provider_id>/resources/requirement/<requirement_id>/<preview_type>')
class ResourcePreviewSmallLarge(OslcResource):

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
class RootServices(OslcResource):

    def get(self):

        """
        Generate Rootservices response
        :return:
        """
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
class ConfigurationCatalog(OslcResource):

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
class ConfigurationComponent(OslcResource):

    def get(self):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        components_url = urlparse(base_url).geturl()

        response = make_response(render_template('pyoslc_oauth/components.html',
                                                 dialog=components_url.replace('components', 'selection')))

        response.headers['max-age'] = '0'
        response.headers['pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Content-Length'] = len(response.data)
        response.headers['Content-Type'] = 'application/rdf+xml;charset=UTF-8'
        response.headers['OSLC-Core-Version'] = "2.0"

        return response


@adapter_ns.route('/config/publisher')
class ConfigurationPublisher(OslcResource):

    def get(self):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        components_url = urlparse(base_url).geturl()

        response = make_response(render_template('pyoslc_oauth/publisher.html',
                                                 about=components_url))

        response.headers['max-age'] = '0'
        response.headers['pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Content-Length'] = len(response.data)
        response.headers['Content-Type'] = 'application/rdf+xml;charset=UTF-8'
        response.headers['OSLC-Core-Version'] = "2.0"

        return response


@adapter_ns.route('/config/selection')
class ConfigurationSelection(OslcResource):

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

            return {"oslc:results": result}

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
class ConfigurationStream(OslcResource):

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
class Source(OslcResource):

    def get(self):
        response = make_response(render_template('pyoslc_oauth/scr.html'))
        return response
