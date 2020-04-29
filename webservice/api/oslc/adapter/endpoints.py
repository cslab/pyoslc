from urlparse import urlparse

from flask import make_response, request, url_for
from flask_restplus import Resource, Namespace
from rdflib import Graph

from webservice.api.oslc.adapter.services import ServiceProviderCatalogSingleton, RootServiceSingleton

adapter_ns = Namespace(name='adapter', description='Python OSLC Adapter', path='/services', )


class OslcResource(Resource):

    def __init__(self, *args, **kwargs):
        super(OslcResource, self).__init__(*args, **kwargs)
        self.graph = kwargs.get('graph', Graph())

    def create_response(self, graph):

        # Getting the content-type for checking the
        # response we will use to serialize the RDF response.
        content_type = request.headers['accept']
        if content_type in ('application/json-ld', 'application/json', '*/*'):
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
