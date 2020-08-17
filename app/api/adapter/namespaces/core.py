import csv
import os
import shutil
from tempfile import NamedTemporaryFile
from urlparse import urlparse

from flask import request, make_response, url_for, render_template, Response, jsonify
from flask_restx import Namespace, Resource
from rdflib import Graph, RDF, RDFS, DCTERMS
from rdflib.plugin import register
from rdflib.serializer import Serializer

from app.api.adapter.mappings.specification import specification_map
from app.api.adapter.namespaces.business import get_requirement_list
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
        # self.logger.debug('Instantiating Resource {}'.format(self))

        self.graph = kwargs.get('graph', Graph())
        self.graph.bind('oslc', OSLC)
        self.graph.bind('rdf', RDF)
        self.graph.bind('rdfs', RDFS)
        self.graph.bind('dcterms', DCTERMS)
        self.graph.bind('j.0', JAZZ_PROCESS)

    def create_response(self, graph, rdf_format=None):

        # Getting the content-type for checking the
        # response we will use to serialize the RDF response.
        content_type = request.headers['accept'] if rdf_format is None else unicode(rdf_format)

        if content_type in ('application/json-ld', 'application/ld+json', 'application/json', '*/*'):
            # If the content-type is any kind of json,
            # we will use the json-ld format for the response.
            content_type = 'json-ld'

        if content_type in ('application/xml', 'application/rdf+xml'):
            content_type = 'pretty-xml'

        if content_type in 'rootservices-xml':
            content_type = 'rootservices-xml'
        elif content_type in 'config-xml':
            content_type = 'config-xml'
        else:
            content_type = 'pretty-xml'

        data = graph.serialize(format=content_type)

        # Sending the response to the client
        response = make_response(data.decode('utf-8'), 200)
        response.headers['Content-Type'] = 'application/rdf+xml;charset=UTF-8'
        response.headers['OSLC-Core-Version'] = "2.0"

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


@adapter_ns.route('/provider/<string:service_provider_id>')
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
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        data = get_requirement_list(base_url)
        response_info = ResponseInfo()
        response_info.total_count = len(data)

        graph = response_info.to_rdf(self.graph)

        return self.create_response(graph=data)

    @adapter_ns.expect(specification)
    def post(self, service_provider_id):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        attributes = specification_map

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


@adapter_ns.route('/provider/<service_provider_id>/resources/requirement/<requirement_id>')
class ResourcePreview(OslcResource):

    def get(self, service_provider_id, requirement_id):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id, requirement_id=requirement_id   )
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        print(request.headers)

        compact = Compact(about=base_url)
        compact.title = 'title'
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

        # return self.create_response(graph=self.graph, rdf_format='pretty-xml')
        # return render_template('pyoslc_oauth/compact.html', compact=compact)

        response = make_response(render_template('pyoslc_oauth/compact.html',
                                                 compact=compact))
        response.headers['max-age'] = '0'
        response.headers['pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Content-Type'] = 'application/x-oslc-compact+xml  ;charset=UTF-8'
        response.headers['OSLC-Core-Version'] = "2.0"

        return response

    @adapter_ns.expect(specification)
    def post(self, service_provider_id):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        attributes = specification_map

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


@adapter_ns.route('/provider/<service_provider_id>/resources/requirement/<requirement_id>/smallPreview')
class ResourcePreviewSmallLarge(OslcResource):

    def get(self, service_provider_id, requirement_id):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id, requirement_id=requirement_id   )
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        response = make_response(render_template("dialogs/smallpreview.html", title='small'))
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

        # response = render_template(
        #     'pyoslc_oauth/rootservices.html',
        #     about=root_services.about,
        #     catalogUri=url_for('oslc.adapter_service_provider_catalog', _external=True),
        #     configUri=url_for('oslc.adapter_configuration_catalog', _external=True),
        #     authDomain=url_for('oslc.doc', _external=True),
        #     requestKey=url_for('consumer.register', _external=True),
        #     approveKey=url_for('consumer.approve', _external=True),
        #     requestToken=url_for('oauth.issue_token', _external=True),
        #     authorize=url_for('oauth.authorize', _external=True),
        #     accessToken=url_for('oauth.issue_token', _external=True),
        #     publisherUrl=url_for('oslc.adapter_configuration_publisher', _external=True),
        # )
        #
        # return Response(response, content_type='application/rdf+xml')
        return self.create_response(graph=self.graph, rdf_format='rootservices-xml')


# @adapter_ns.route('/publisher')
# class Publisher(OslcResource):
#
#     def get(self):
#         endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
#         base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)
#         publisher_url = urlparse(base_url).geturl()
#
#         publisher = PublisherSingleton.get_publisher(publisher_url)
#
#         publisher.to_rdf(self.graph)
#
#         return self.create_response(graph=self.graph, rdf_format='pretty-xml')


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
                    'rdf:resource': 'http://192.168.1.66:5000/oslc/services/config/stream/1',
                    'rdf:type': 'http://open-services.net/ns/config#Stream'

                },
                {
                    'oslc:label': 'PyOSLC Stream 2',
                    'rdf:resource': 'http://192.168.1.66:5000/oslc/services/config/stream/2',
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
                                                 selection_url=url_for('oslc.adapter_configuration_selection', _external=True),
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
