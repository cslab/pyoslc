from flask import make_response, request
from flask_restplus import Resource, reqparse
from rdflib import Graph
from rdflib.namespace import DCTERMS

from pyoslc.vocabulary import OSLCCore
from webservice.api.oslc.adapter.definitions import service_provider_catalog, publisher
from webservice.api.oslc.adapter.definitions import service_provider, service
from webservice.api.oslc.adapter.definitions import query_capability, creation_factory
from webservice.api.oslc.rm.business import get_requirement_list


class ServiceProviderCatalog(Resource):

    def __init__(self, *args, **kwargs):
        super(ServiceProviderCatalog, self).__init__(*args, **kwargs)
        self.graph = kwargs['graph']

    def get(self):
        is_human_client = request.headers['accept'].__contains__('*/*')

        content_type = 'text/turtle'
        graph = Graph()
        graph.bind('oslc', OSLCCore, override=False)
        graph.bind('dcterms', DCTERMS, override=False)

        service_provider_catalog.to_rdf(graph)
        data = graph.serialize(format=content_type)

        # Sending the response to the client
        response = make_response(data.decode('utf-8'), 200)
        response.headers['Content-Type'] = content_type
        response.headers['Oslc-Core-Version'] = "2.0"

        return response


class ServiceProvider(Resource):

    def __init__(self, *args, **kwargs):
        super(ServiceProvider, self).__init__(*args, **kwargs)
        self.graph = kwargs['graph']

    def get(self, service_provider_id):
        content_type = 'text/turtle'
        graph = Graph()
        graph.bind('oslc', OSLCCore, override=False)
        graph.bind('dcterms', DCTERMS, override=False)

        service_provider.to_rdf(graph)
        data = graph.serialize(format=content_type)

        # Sending the response to the client
        response = make_response(data.decode('utf-8'), 200)
        response.headers['Content-Type'] = content_type
        response.headers['Oslc-Core-Version'] = "2.0"

        return response


class Service(Resource):

    def get(self, service_id):
        content_type = 'text/turtle'
        graph = Graph()

        service.to_rdf(graph)
        data = graph.serialize(format=content_type)

        # Sending the response to the client
        response = make_response(data.decode('utf-8'), 200)
        response.headers['Content-Type'] = content_type
        response.headers['Oslc-Core-Version'] = "2.0"

        return response


class QueryCapability(Resource):

    def get(self, query_capability_id):

        post_parser = reqparse.RequestParser()
        post_parser.add_argument('oslc.where', dest='where', location='form', required=False, help='where clause for the query')
        post_parser.add_argument('page', location='form', required=False, help='page of the list')
        post_parser.add_argument('limit', location='form', required=False, help='number of elements')

        content_type = 'text/turtle'
        # graph = Graph()

        # method to retrieve information from the requirement csv file
        # then convert this requirement to and RDF format
        # then convert the rdf-req to a response

        graph = get_requirement_list(request.base_url)

        # query_capability.to_rdf(graph)
        data = graph.serialize(format=content_type)

        # Sending the response to the client
        response = make_response(data.decode('utf-8'), 200)
        response.headers['Content-Type'] = content_type
        response.headers['Oslc-Core-Version'] = "2.0"

        return response


class CreationFactory(Resource):

    def get(self, creation_factory_id):
        content_type = 'text/turtle'
        graph = Graph()

        creation_factory.to_rdf(graph)
        data = graph.serialize(format=content_type)

        # Sending the response to the client
        response = make_response(data.decode('utf-8'), 200)
        response.headers['Content-Type'] = content_type
        response.headers['Oslc-Core-Version'] = "2.0"

        return response

    def post(self):
        return make_response('{}', 200)


class Publisher(Resource):

    def get(self):
        content_type = 'text/turtle'
        graph = Graph()

        publisher.to_rdf(graph)
        data = graph.serialize(format=content_type)

        # Sending the response to the client
        response = make_response(data.decode('utf-8'), 200)
        response.headers['Content-Type'] = content_type
        response.headers['Oslc-Core-Version'] = "2.0"

        return response
