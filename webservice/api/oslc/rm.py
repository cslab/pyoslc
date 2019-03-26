from flask import make_response, request
from flask_restplus import Namespace, Resource
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCTERMS, RDF
from rdflib.plugin import PluginException

from pyoslc.resource import OSLC, ServiceProviderCatalog
from pyoslc.vocabulary.rm import OSLC_RM
from webservice.api.oslc import api

rm_ns = Namespace(name='rm', description='Requirements Management', path='/rm')


@rm_ns.route('/rootservices')
@api.representation('application/rdf+xml')
@api.representation('application/json-ld')
@api.representation('text/turtle')
class RootServices(Resource):

    # __pyoslc = PyOSLC()
    graph = Graph()

    graph.bind('oslc_rm', OSLC_RM)

    @rm_ns.doc(responses={200: 'The rootservices RDF response for the Requirements Management application.'})
    # @__pyoslc.catalog(__graph)
    def get(cls):
        content_type = request.headers['accept']

        cls.graph.bind('dcterms', DCTERMS, override=False)
        cls.graph.bind('oslc', OSLC, override=False)
        cls.graph.bind('oslc_rm', OSLC_RM, override=False)

        spc = URIRef("http://examples.org/oslc/catalog")
        cls.graph.add((spc, RDF.type, OSLC.ServiceProviderCatalog))
        cls.graph.add((spc, DCTERMS.title, Literal("Service Provider Catalog")))
        cls.graph.add((spc, DCTERMS.description, Literal("This is the master catalog")))

        sp = URIRef("http://examples.org/oslc/catalog/serviceProvider")
        cls.graph.add((sp, RDF.type, OSLC.ServiceProvider))
        cls.graph.add((sp, DCTERMS.title, Literal("Service Provider for RDF Store")))
        cls.graph.add((sp, DCTERMS.description, Literal("Service Provider for managint RDF Store")))
        cls.graph.add((sp, OSLC.details, sp))

        try:
            if content_type == 'application/json-ld':
                content_type = 'json-ld'

            data = cls.graph.serialize(format=content_type)

        except PluginException as e:
            return 'Content-Type Incompatible', 500

        response = make_response(data.decode('utf-8'), 200)
        response.headers['Content-Type'] = content_type
        response.headers['Oslc-Core-Version'] = "2.0"

        return response


@rm_ns.route('/catalog')
class Catalog(Resource):

    def get(self):
        return make_response('{}', 200)

#     def post(self):
#         return make_response('{}', 200)
#
#     def put(self):
#         return make_response('{}', 200)
#
#     def delete(self):
#         return make_response('{}', 200)


api.add_namespace(rm_ns)
