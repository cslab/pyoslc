from flask import Blueprint
from flask_restplus import Api

bp = Blueprint('oslc', __name__, '/oslc')

api = Api(
    app=bp,
    version='1.0.0',
    title='Python OSLC API',
    description='Implementation for the OSLC specification for python application',
    default_mediatype='application/rdf+xml',
    contact='Contact Software & Koneksys',
    contact_url='https://www.contact-software.com/en/',
    contact_email="mario.carrasco@koneksys.com"
)


from webservice.api.oslc.rm import rm_ns
from webservice.api.oslc.cm import cm_ns


# api.add_namespace(rm_ns)
# api.add_namespace(cm_ns)


# @api.route('/example')
# @api.representation('application/rdf+xml')
# @api.representation('text/turtle')
# class Example(Resource):
#     def get(self):

#

#
#         s = URIRef("http://examples.org/oslc/catalog/serviceProvider/service")
#         g.add((s, RDF.type, OSLC.Service))
#         g.add((s, DCTERMS.title, Literal("Service for main operations")))
#         g.add((s, DCTERMS.description, Literal("Service for Factories and Capabilities")))
#
#         c = URIRef("http://examples.org/oslc/catalog/rdfstores/service/creation")
#         g.add((c, RDF.type, OSLC.CreationFactory))
#         g.add((c, OSLC.creation, URIRef("http://examples.org/oslc/catalog/serviceProvider/service/creation")))
#         g.add((c, DCTERMS.title, Literal("Creation Factory")))
#         g.add((c, DCTERMS.description, Literal("Service for creating resources")))
#
#         q = URIRef("http://examples.org/oslc/catalog/serviceProvider/service/query")
#         g.add((q, RDF.type, OSLC.QueryCapability))
#         g.add((q, OSLC.queryBase, URIRef("http://examples.org/oslc/catalog/serviceProvider/service/query")))
#         g.add((q, DCTERMS.title, Literal("Query Capability")))
#         g.add((q, DCTERMS.description, Literal("Service for retrieving information.")))
#
#         g.add((s, OSLC.queryCapability, q))
#         g.add((s, OSLC.creationFactory, c))
#         g.add((sp, OSLC.service, s))
#         g.add((spc, OSLC.ServiceProvider, sp))
#
#         try:
#             if content_type == 'application/json-ld':
#                 content_type = 'json-ld'
#
#             data = g.serialize(format=content_type)
#         except PluginException as e:
#             return 'Content-Type Incompatible', 500
#
#         response = make_response(data.decode('utf-8'), 200)
#         response.headers['Content-Type'] = content_type
#
#         return response



