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


@rm_ns.route('/requirement')
@api.representation('application/rdf+xml')
@api.representation('application/json-ld')
@api.representation('text/turtle')
class Requirement(Resource):

    def get(self):
        """
        Listing the Specification statements on the RDF format using the RM domain
        :return: A RDF formatted of the Requirements.
        """

        try:
            content_type = request.headers['accept']
            if content_type in ('application/json-ld', 'application/json'):
                content_type = 'json-ld'

            # Loading information from the specification.csv file
            # located on the examples folder of the pyoslc project.

            path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')

            with open(path, 'rb') as f:
                reader = csv.DictReader(f, delimiter=';')

                graph = Graph()

                for row in reader:
                    rq = RQ()
                    rq.update(row)
                    graph += rq.to_rdf()

            data = graph.serialize(format=content_type)

            response = make_response(data.decode('utf-8'), 200)
            response.headers['Content-Type'] = content_type
            response.headers['Oslc-Core-Version'] = "2.0"

            return response

        except PluginException as pe:
            current_app.logger.info(pe.message)
            return 'Content-Type {} Incompatible'.format(content_type), 500
        except Exception as e:
            current_app.logger.info(e.message)
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

