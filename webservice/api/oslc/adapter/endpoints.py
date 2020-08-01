import csv
import logging
import os
import shutil
from tempfile import NamedTemporaryFile
from urlparse import urlparse

from flask import make_response, request, url_for, render_template
from flask_restplus import Namespace, Resource

from rdflib import Graph
from rdflib.namespace import DCTERMS, RDF, RDFS
from rdflib.plugin import register
from rdflib.serializer import Serializer

from pyoslc.resources.domains.rm import Requirement
from pyoslc.vocabulary import OSLCCore
from pyoslc.vocabulary.jazz import JAZZ_PROCESS
from webservice.api.oslc.adapter.resources.resource_service import config_service_resource
from webservice.api.oslc.adapter.services.providers import ServiceProviderCatalogSingleton, RootServiceSingleton
from webservice.api.oslc.adapter.services.specification import ServiceResource
from webservice.api.oslc.rm.models import specification

adapter_ns = Namespace(name='adapter', description='Python OSLC Adapter', path='/services', )

register(
    'rootservices-xml', Serializer,
    'pyoslc.serializers.jazzxml', 'JazzRootServiceSerializer'
)

config_service_resource(
    'specification', ServiceResource,
    'webservice.api.oslc.adapter.services.specification', 'Specification',
)


class OslcResource(Resource):

    def __init__(self, *args, **kwargs):
        super(OslcResource, self).__init__(*args, **kwargs)

        self.logger = logging.getLogger('flask.app')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            self.logger.addHandler(handler)

        self.logger.debug('Instantiating Resource {}'.format(self))

        self.graph = kwargs.get('graph', Graph())
        self.graph.bind('oslc', OSLCCore)
        self.graph.bind('rdf', RDF)
        self.graph.bind('rdfs', RDFS)
        self.graph.bind('dcterms', DCTERMS)
        self.graph.bind('j.0', JAZZ_PROCESS)

    def create_response(self, graph):

        # Getting the content-type for checking the
        # response we will use to serialize the RDF response.
        content_type = request.headers['accept']

        if content_type in ('application/json-ld', 'application/ld+json', 'application/json', '*/*'):
            # If the content-type is any kind of json,
            # we will use the json-ld format for the response.
            content_type = 'json-ld'

        if content_type in ('application/xml', 'application/rdf+xml'):
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
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint), service_provider_id=service_provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        url = urlparse(base_url)

        provider = ServiceProviderCatalogSingleton.get_provider(request, service_provider_id)
        provider.to_rdf(self.graph)
        return self.create_response(graph=self.graph)


@adapter_ns.route('/provider/<string:service_provider_id>/resources/requirement')
class QC(OslcResource):

    def get(self, service_provider_id):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        from webservice.api.oslc.rm.business import get_requirement_list
        data = get_requirement_list(base_url)

        return self.create_response(graph=data)

    @adapter_ns.expect(specification)
    def post(self, service_provider_id):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint),
                               service_provider_id=service_provider_id)
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        from webservice.api.oslc.adapter.mappings.specification import specification_map
        attributes = specification_map

        from webservice.api.oslc.rm.parsers import specification_parser
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


# @adapter_ns.route('/project/<service_provider_id>/resources/requirement/<requirement_id>')
# class RS(OslcResource):
#     def get(self, service_provider_id, requirement_id):
#         graph = self.graph
#         graph.bind('oslc_rm', OSLC_RM.uri)
#
#         url = 'http://baseurl/oslc/services/project/{}/resources/requirement/{}'.format(service_provider_id, requirement_id)
#
#         rs = RSRC(graph, URIRef(url))
#         rs.add(RDF.type, OSLC_RM.Requirement)
#         rs.add(DCTERMS.identifier, Literal(requirement_id, datatype=XSD.Literal))
#         rs.add(DCTERMS.title, Literal("The ACRV shall provide medical life-support accommodations for one crew member", datatype=XSD.Literal))
#         rs.add(DCTERMS.project, Literal("Project-1", datatype=XSD.Literal))
#         rs.add(DCTERMS.creator, Literal("Mario", datatype=XSD.Literal))
#         # rs.add(OSLC_RM.elaboratedBy, Literal("Ian Altman", datatype=XSD.Literal))
#         rs.add(OSLCCore.shortTitle, Literal("SDK-Dev", datatype=XSD.Literal))
#         rs.add(OSLCCore.serviceProvider, URIRef('http://baseurl/oslc/services/catalog/' + service_provider_id))
#
#         #
#         # <http://localhost:5000/oslc/rm/requirement/X1C2V3B1> a ns1:Requirement ;
#         #     ns1:affectedBy "0" ;
#         #     ns1:constrainedBy "Customer Requirement" ;
#         #     ns1:decomposedBy "Draft" ;
#         #     ns1:satisfiedBy "Software Development" ;
#         #     ns1:trackedBy "0" ;
#         #     ns1:validatedBy "1" ;
#         #     ns2:creator "" ;
#         #     ns2:description "The OSLC RM Specification needs to be awesome 1" ;
#         #     ns2:shortTitle "SDK-Dev" ;
#         #     ns2:subject "Project-1" ;
#         #     ns2:title "The ACRV shall provide medical life-support accommodations for one crew member" .
#         #
#         return self.create_response(graph=self.graph)


@adapter_ns.route('/rootservices')
class RootServices(OslcResource):

    def get(self):

        """
        g = Graph()
        data = g.serialize(format='application/rdf+xml')

        return make_response(data.decode('utf-8'), 200)
        :return:
        """
        root_services = RootServiceSingleton.get_root_service()
        root_services.about = request.base_url
        root_services.to_rdf(self.graph)

        response = render_template(
            'oauth/rootservices.html',
            about=root_services.about,
            catalogUri=url_for('oslc.adapter_service_provider_catalog', _external=True),
            authDomain=url_for('web.index', _external=True),
            requestKey=url_for('consumer.register', _external=True),
            approveKey=url_for('consumer.approve', _external=True),
            requestToken=url_for('oauth.issue_token', _external=True),
            authorize=url_for('oauth.authorize', _external=True),
            accessToken=url_for('oauth.issue_token', _external=True)

        )

        # return Response(response, content_type='application/rdf+xml')
        return self.create_response(graph=self.graph, format='rootservices-xml')




# # class Service(Resource):
# #
# #     def get(self, service_id):
# #         content_type = 'text/turtle'
# #         graph = Graph()
# #
# #         service.to_rdf(graph)
# #         data = graph.serialize(format=content_type)
# #
# #         # Sending the response to the client
# #         response = make_response(data.decode('utf-8'), 200)
# #         response.headers['Content-Type'] = content_type
# #         response.headers['Oslc-Core-Version'] = "2.0"
# #
# #         return response
# #
# #
# # class QueryCapability(Resource):
# #
# #     def get(self, query_capability_id):
# #
# #         post_parser = reqparse.RequestParser()
# #         post_parser.add_argument('oslc.where', dest='where', location='form',
# #                                  required=False, help='where clause for the query')
# #         post_parser.add_argument(
# #             'page', location='form', required=False, help='page of the list')
# #         post_parser.add_argument(
# #             'limit', location='form', required=False, help='number of elements')
# #
# #         content_type = 'text/turtle'
# #         # graph = Graph()
# #
# #         # method to retrieve information from the requirement csv file
# #         # then convert this requirement to and RDF format
# #         # then convert the rdf-req to a response
# #
# #         graph = get_requirement_list(request.base_url)
# #
# #         # query_capability.to_rdf(graph)
# #         data = graph.serialize(format=content_type)
# #
# #         # Sending the response to the client
# #         response = make_response(data.decode('utf-8'), 200)
# #         response.headers['Content-Type'] = content_type
# #         response.headers['Oslc-Core-Version'] = "2.0"
# #
# #         return response
# # class Publisher(Resource):
# #
# #     def get(self):
# #         content_type = 'text/turtle'
# #         graph = Graph()
# #
# #         publisher.to_rdf(graph)
# #         data = graph.serialize(format=content_type)
# #
# #         # Sending the response to the client
# #         response = make_response(data.decode('utf-8'), 200)
# #         response.headers['Content-Type'] = content_type
# #         response.headers['Oslc-Core-Version'] = "2.0"
# #
# #         return response
