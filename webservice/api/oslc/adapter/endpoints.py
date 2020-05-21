from urlparse import urlparse

from rdflib.resource import Resource as RSRC
from flask import make_response, request, url_for
from flask_restplus import Resource, Namespace
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD

from pyoslc.vocabulary import OSLCCore
from pyoslc.vocabulary.rm import OSLC_RM
from webservice.api.oslc.adapter.services import ServiceProviderCatalogSingleton, RootServiceSingleton

adapter_ns = Namespace(name='adapter', description='Python OSLC Adapter', path='/services', )


class OslcResource(Resource):

    def __init__(self, *args, **kwargs):
        super(OslcResource, self).__init__(*args, **kwargs)
        self.graph = kwargs.get('graph', Graph())
        self.graph.bind('oslc', OSLCCore.uri)
        self.graph.bind('dcterms', DCTERMS)

    def create_response(self, graph):

        # Getting the content-type for checking the
        # response we will use to serialize the RDF response.
        content_type = request.headers['accept']
        if content_type in ('application/json-ld', 'application/ld+json', 'application/json', '*/*'):
            # If the content-type is any kind of json,
            # we will use the json-ld format for the response.
            content_type = 'json-ld'

        data = graph.serialize(format=content_type)

        # print(data)

        # Sending the response to the client
        response = make_response(data.decode('utf-8'), 200)
        response.headers['Content-Type'] = content_type
        response.headers['Oslc-Core-Version'] = "2.0"

        return response


@adapter_ns.route('/catalog')
class ServiceProviderCatalog(OslcResource):

    def __init__(self, *args, **kwargs):
        super(ServiceProviderCatalog, self).__init__(*args, **kwargs)

    def get(self):
        endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
        base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)

        catalog_url = urlparse(base_url).geturl()
        catalog_url = catalog_url.replace('localhost:5000', 'baseurl')
        catalog_url = catalog_url.replace('127.0.0.1:5000', 'baseurl')
        catalog_url = catalog_url.replace('0.0.0.0:5000', 'baseurl')

        catalog = ServiceProviderCatalogSingleton.get_catalog(catalog_url)
        catalog.to_rdf(self.graph)
        return self.create_response(graph=self.graph)


@adapter_ns.route('/<string:service_provider_id>')
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


@adapter_ns.route('/<string:service_provider_id>/requirement')
class IoTPlatformService(OslcResource):

    def get(self):
        return self.create_response(graph=self.graph)


# @adapter_ns.route('/catalog/id/<string:service_provider_id>')
class SP(OslcResource):

    def get(self):
        # Here we will retrieve information using the Repository pattern

        pass


@adapter_ns.route('/project/<string:service_provider_id>/resources/requirement')
class QC(OslcResource):
    def get(self, service_provider_id):
        graph = self.graph

        url = 'http://baseurl/oslc/services/project/{}/resources/requirement'.format(service_provider_id)
        ri = RSRC(graph, URIRef(url))
        ri.add(RDF.type, URIRef(OSLCCore.ResponseInfo))

        ri1 = RSRC(ri, URIRef(url + '/X1C2V3B1'))
        ri2 = RSRC(ri, URIRef(url + '/X1C2V3B2'))
        ri3 = RSRC(ri, URIRef(url + '/X1C2V3B3'))

        ri.add(RDFS.member, ri1.identifier)
        ri.add(RDFS.member, ri2.identifier)
        ri.add(RDFS.member, ri3.identifier)
        ri.add(OSLCCore.totalCount, Literal("03", datatype=XSD.integer))

        return self.create_response(graph=self.graph)


@adapter_ns.route('/project/<service_provider_id>/resources/requirement/<requirement_id>')
class RS(OslcResource):
    def get(self, service_provider_id, requirement_id):
        graph = self.graph
        graph.bind('oslc_rm', OSLC_RM.uri)

        url = 'http://baseurl/oslc/services/project/{}/resources/requirement/{}'.format(service_provider_id, requirement_id)

        rs = RSRC(graph, URIRef(url))
        rs.add(RDF.type, OSLC_RM.Requirement)
        rs.add(DCTERMS.identifier, Literal(requirement_id, datatype=XSD.Literal))
        rs.add(DCTERMS.title, Literal("The ACRV shall provide medical life-support accommodations for one crew member", datatype=XSD.Literal))
        rs.add(DCTERMS.project, Literal("Project-1", datatype=XSD.Literal))
        rs.add(DCTERMS.creator, Literal("Mario", datatype=XSD.Literal))
        # rs.add(OSLC_RM.elaboratedBy, Literal("Ian Altman", datatype=XSD.Literal))
        rs.add(OSLCCore.shortTitle, Literal("SDK-Dev", datatype=XSD.Literal))
        rs.add(OSLCCore.serviceProvider, URIRef('http://baseurl/oslc/services/catalog/' + service_provider_id))

        #
        # <http://localhost:5000/oslc/rm/requirement/X1C2V3B1> a ns1:Requirement ;
        #     ns1:affectedBy "0" ;
        #     ns1:constrainedBy "Customer Requirement" ;
        #     ns1:decomposedBy "Draft" ;
        #     ns1:satisfiedBy "Software Development" ;
        #     ns1:trackedBy "0" ;
        #     ns1:validatedBy "1" ;
        #     ns2:creator "" ;
        #     ns2:description "The OSLC RM Specification needs to be awesome 1" ;
        #     ns2:shortTitle "SDK-Dev" ;
        #     ns2:subject "Project-1" ;
        #     ns2:title "The ACRV shall provide medical life-support accommodations for one crew member" .
        #
        return self.create_response(graph=self.graph)


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
        root_services.to_rdf(self.graph)

        return self.create_response(graph=self.graph)




# class Service(Resource):
#
#     def get(self, service_id):
#         content_type = 'text/turtle'
#         graph = Graph()
#
#         service.to_rdf(graph)
#         data = graph.serialize(format=content_type)
#
#         # Sending the response to the client
#         response = make_response(data.decode('utf-8'), 200)
#         response.headers['Content-Type'] = content_type
#         response.headers['Oslc-Core-Version'] = "2.0"
#
#         return response
#
#
# class QueryCapability(Resource):
#
#     def get(self, query_capability_id):
#
#         post_parser = reqparse.RequestParser()
#         post_parser.add_argument('oslc.where', dest='where', location='form',
#                                  required=False, help='where clause for the query')
#         post_parser.add_argument(
#             'page', location='form', required=False, help='page of the list')
#         post_parser.add_argument(
#             'limit', location='form', required=False, help='number of elements')
#
#         content_type = 'text/turtle'
#         # graph = Graph()
#
#         # method to retrieve information from the requirement csv file
#         # then convert this requirement to and RDF format
#         # then convert the rdf-req to a response
#
#         graph = get_requirement_list(request.base_url)
#
#         # query_capability.to_rdf(graph)
#         data = graph.serialize(format=content_type)
#
#         # Sending the response to the client
#         response = make_response(data.decode('utf-8'), 200)
#         response.headers['Content-Type'] = content_type
#         response.headers['Oslc-Core-Version'] = "2.0"
#
#         return response
#
#
# class CreationFactory(Resource):
#
#     def get(self, creation_factory_id):
#         content_type = 'text/turtle'
#         graph = Graph()
#
#         creation_factory.to_rdf(graph)
#         data = graph.serialize(format=content_type)
#
#         # Sending the response to the client
#         response = make_response(data.decode('utf-8'), 200)
#         response.headers['Content-Type'] = content_type
#         response.headers['Oslc-Core-Version'] = "2.0"
#
#         return response
#
#     def post(self):
#         return make_response('{}', 200)
#
#
# class Publisher(Resource):
#
#     def get(self):
#         content_type = 'text/turtle'
#         graph = Graph()
#
#         publisher.to_rdf(graph)
#         data = graph.serialize(format=content_type)
#
#         # Sending the response to the client
#         response = make_response(data.decode('utf-8'), 200)
#         response.headers['Content-Type'] = content_type
#         response.headers['Oslc-Core-Version'] = "2.0"
#
#         return response
