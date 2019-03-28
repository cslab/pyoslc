import csv
import os

from flask import make_response, request, current_app
from flask_restplus import Namespace, Resource, abort
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCTERMS, RDF
from rdflib.plugin import PluginException

from pyoslc.vocabulary import OSLCCore
from pyoslc.vocabulary.rm import OSLC_RM
from webservice.api.oslc import api, parsers
from webservice.api.oslc.models import requirement, specification
from pyoslc.resources.requirement import Requirement as RQ

rm_ns = Namespace(name='rm', description='Requirements Management', path='/rm')


@rm_ns.route('/rootservices')
@api.representation('application/rdf+xml')
@api.representation('application/json-ld')
@api.representation('text/turtle')
@api.consume('application/rdf+xml')
@api.consume('application/json-ld')
@api.consume('text/turtle')
class RootServices(Resource):

    graph = Graph()
    graph.bind('oslc_rm', OSLC_RM)

    @rm_ns.doc(responses={200: 'The rootservices RDF response for the Requirements Management application.'})
    def get(cls):
        content_type = request.headers['accept']

        cls.graph.bind('dcterms', DCTERMS, override=False)
        cls.graph.bind('oslc', OSLCCore, override=False)
        cls.graph.bind('oslc_rm', OSLC_RM, override=False)

        spc = URIRef("http://examples.org/oslc/catalog")
        cls.graph.add((spc, RDF.type, OSLCCore.ServiceProviderCatalog))
        cls.graph.add((spc, DCTERMS.title, Literal("Service Provider Catalog")))
        cls.graph.add((spc, DCTERMS.description, Literal("This is the master catalog")))

        sp = URIRef("http://examples.org/oslc/catalog/serviceProvider")
        cls.graph.add((sp, RDF.type, OSLCCore.ServiceProvider))
        cls.graph.add((sp, DCTERMS.title, Literal("Service Provider for RDF Store")))
        cls.graph.add((sp, DCTERMS.description, Literal("Service Provider for managint RDF Store")))
        cls.graph.add((sp, OSLCCore.details, sp))

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


@rm_ns.route('/requirement')
class Requirement(Resource):

    def get(self):
        """
        Listing the Specification statements on the RDF format using the RM domain
        :return: A RDF formatted of the Requirements.
        """

        try:
            content_type = request.headers['accept']
            if content_type == 'application/json-ld':
                content_type = 'json-ld'

            path = os.path.join(current_app.instance_path, 'medias/') + 'custom_file_name.csv'

            with open(path, 'rb') as f:
                reader = csv.DictReader(f, delimiter=';')

                requirements = []
                for row in reader:
                    requirements.append(row)

                    rq = RQ()
                    rq.update(row)

                    graph = rq.to_rdf()

            data = graph.serialize(format=content_type)

            response = make_response(data.decode('utf-8'), 200)
            response.headers['Content-Type'] = content_type
            response.headers['Oslc-Core-Version'] = "2.0"

            return response

        except Exception as e:
            print e.message
            abort(404)

    @api.expect(specification)
    @api.marshal_with(requirement, envelope='resource')
    def post(self):
        # requirement = convert(data)
        # TODO convert the requirement object, to RDF.

        return make_response('{}', 200)

    @staticmethod
    def get_map(field_names):

        data = dict()

        for field in field_names:
            print(field)
            print(dict)

        return data


@rm_ns.route('/collection')
class RequirementCollection(Resource):

    @api.expect(parsers.csv_file_upload)
    def post(self):
        args = parsers.csv_file_upload.parse_args()
        if args['csv_file'].mimetype in ('application/xls', 'text/csv'):
            destination = os.path.join(current_app.instance_path, 'medias/')
            if not os.path.exists(destination):
                os.makedirs(destination)
            csv_file = '%s%s' % (destination, 'custom_file_name.csv')
            args['csv_file'].save(csv_file)


            # TODO take each line of CSV to process for RDF format


        else:
            abort(404)

        return {'status': 'Done'}


api.add_namespace(rm_ns)

