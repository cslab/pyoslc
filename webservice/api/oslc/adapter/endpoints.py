from flask import make_response
from flask_restplus import Resource
from rdflib import Graph

from webservice.api.oslc.adapter.definitions import service_provider_catalog, service_provider, service, \
    query_capability, creation_factory


class ServiceProviderCatalog(Resource):

    def get(self):

        content_type = 'text/turtle'
        graph = Graph()

        service_provider_catalog.to_rdf(graph)
        data = graph.serialize(format=content_type)

        # Sending the response to the client
        response = make_response(data.decode('utf-8'), 200)
        response.headers['Content-Type'] = content_type
        response.headers['Oslc-Core-Version'] = "2.0"

        return response


class ServiceProvider(Resource):

    def get(self, service_provider_id):
        content_type = 'text/turtle'
        graph = Graph()

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
        content_type = 'text/turtle'
        graph = Graph()

        query_capability.to_rdf(graph)
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
