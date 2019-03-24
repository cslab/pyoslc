from flask import Blueprint, request, make_response
from flask_restplus import Api, Resource
from rdflib import Graph, URIRef, RDF, Literal
from rdflib.namespace import DCTERMS, Namespace
from rdflib.plugin import PluginException

bp = Blueprint('oslc', __name__, '/oslc')


api = Api(
    app=bp,
    version='1.0.0',
    title='Python OSLC API',
    description='Implementation for the OSLC specification for python application',
    default_mediatype='application/rdf+xml')


@api.route('/catalog')
@api.representation('application/json-ld')
@api.representation('application/rdf+xml')
@api.representation('text/turtle')
class Catalog(Resource):
    """
    Service Provider Catalog
    """

    @api.doc(responses={200: 'The Service Provider Catalog description for the Dataset.'})
    def get(self):
        """
        The endpoint for creating the ServiceProviderCatalog.

        The information will be related with the application
        to find the endpoints required to operate the application.

        :return: The RDF data with the ServiceProviderCatalog descriptor.
        """

        content_type = request.headers['accept']

        OSLC = Namespace("http://open-services.net/ns/core#")

        g = Graph()
        g.bind('oslc', OSLC, override=False)
        g.bind('dcterms', DCTERMS, override=False)

        spc = URIRef("http://examples.org/oslc/catalog")
        g.add((spc, RDF.type, OSLC.ServiceProviderCatalog))
        g.add((spc, DCTERMS.title, Literal("Service Provider Catalog")))
        g.add((spc, DCTERMS.description, Literal("This is the master catalog")))

        sp = URIRef("http://examples.org/oslc/catalog/serviceProvider")
        g.add((sp, RDF.type, OSLC.ServiceProvider))
        g.add((sp, DCTERMS.title, Literal("Service Provider for RDF Store")))
        g.add((sp, DCTERMS.description, Literal("Service Provider for managint RDF Store")))
        g.add((sp, OSLC.details, sp))

        s = URIRef("http://examples.org/oslc/catalog/serviceProvider/service")
        g.add((s, RDF.type, OSLC.Service))
        g.add((s, DCTERMS.title, Literal("Service for main operations")))
        g.add((s, DCTERMS.description, Literal("Service for Factories and Capabilities")))

        c = URIRef("http://examples.org/oslc/catalog/rdfstores/service/creation")
        g.add((c, RDF.type, OSLC.CreationFactory))
        g.add((c, OSLC.creation, URIRef("http://examples.org/oslc/catalog/serviceProvider/service/creation")))
        g.add((c, DCTERMS.title, Literal("Creation Factory")))
        g.add((c, DCTERMS.description, Literal("Service for creating resources")))

        q = URIRef("http://examples.org/oslc/catalog/serviceProvider/service/query")
        g.add((q, RDF.type, OSLC.QueryCapability))
        g.add((q, OSLC.queryBase, URIRef("http://examples.org/oslc/catalog/serviceProvider/service/query")))
        g.add((q, DCTERMS.title, Literal("Query Capability")))
        g.add((q, DCTERMS.description, Literal("Service for retrieving information.")))

        g.add((s, OSLC.queryCapability, q))
        g.add((s, OSLC.creationFactory, c))
        g.add((sp, OSLC.service, s))
        g.add((spc, OSLC.ServiceProvider, sp))

        try:
            if content_type == 'application/json-ld':
                content_type = 'json-ld'

            data = g.serialize(format=content_type)
        except PluginException as e:
            return 'Content-Type Incompatible', 500

        response = make_response(data.decode('utf-8'), 200)
        response.headers['Content-Type'] = content_type

        return response
