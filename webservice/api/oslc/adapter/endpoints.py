from collections import OrderedDict

from flask import make_response, request
from flask_restplus import Resource
from rdflib import URIRef

from pyoslc.resource import ServiceProviderCatalog, Publisher, ServiceProvider


class Catalog(Resource):

    def __init__(self, *args, **kwargs):
        super(Catalog, self).__init__(*args, **kwargs)
        self.base_url = request.base_url
        self.spc = ServiceProviderCatalog(self.base_url + "catalog")

    def get(self):
        is_human_client = request.headers['accept'].__contains__('*/*')

        self.spc.title = "This the service provider title"
        self.spc.description = "This is the description for the service provider"

        publisher = Publisher(self.base_url + "publisher")
        self.spc.publisher = publisher

        domains = OrderedDict()
        domains.update({'jazz': 'http://jazz.net/xmlns/prod/jazz/process/1.0/'})
        domains.update({'iot': 'http://jazz.net/ns/iot#'})
        domains.update({'bmx': 'http://jazz.net/ns/bmx#'})

        self.spc.domain = domains

        spc_ref_1 = ServiceProviderCatalog(self.base_url + "1")
        spc_ref_2 = ServiceProviderCatalog(self.base_url + "2")

        self.spc.add_service_provider_catalog(spc_ref_1)
        self.spc.add_service_provider_catalog(spc_ref_2)

        sp = ServiceProvider(self.base_url + "provider")
        self.spc.add_service_provider(sp)

        data = self.spc.to_rdf()

        # Sending the response to the client
        response = make_response(data.decode('utf-8'), 200)
        response.headers['Content-Type'] = 'application/rdf+xml'
        response.headers['Oslc-Core-Version'] = "2.0"

        return response
