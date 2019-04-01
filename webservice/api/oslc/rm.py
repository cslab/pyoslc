import csv
import os
import shutil
from tempfile import NamedTemporaryFile

from flask import make_response, request, current_app
from flask_restplus import Namespace, Resource, abort
from rdflib import Graph
from rdflib.plugin import PluginException

from webservice.api.oslc import api, parsers
from webservice.api.oslc.models import specification
from pyoslc.resources.requirement import Requirement as RQ
from webservice.api.oslc.parsers import specification_parser

rm_ns = Namespace(name='rm', description='Requirements Management', path='/rm')


@rm_ns.route('/requirement')
@api.representation('application/rdf+xml')
@api.representation('application/json-ld')
@api.representation('text/turtle')
class RequirementList(Resource):

    @rm_ns.response(200, 'The RDF formatted response of the requirements, taken from the specification')
    def get(self):
        """
        Returns the list of Requirements converted from the Specification

        Listing the Specification statements on the RDF format using the RM domain

        :return: A RDF formatted of the Requirements.
        """

        try:
            # Getting the content-type for checking the
            # response we will use to serialize the RDF response.
            content_type = request.headers['accept']
            if content_type in ('application/json-ld', 'application/json'):
                # If the content-type is any kind of json,
                # we will use the json-ld format for the response.
                content_type = 'json-ld'

            # Instantiating the graph where we will store
            # all the requirements from the source (csv file)
            graph = Graph()

            # Loading information from the specification.csv file
            # located on the examples folder of the pyoslc project.
            path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')
            with open(path, 'rb') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    rq = RQ()               # instantiating the Requirement object
                    rq.update(row)          # Parsing the specification to requirement
                    graph += rq.to_rdf()    # Accumulating the triples on the graph

            # Serializing (converting) each triples of the graph
            # on the selected type for the response
            data = graph.serialize(format=content_type)

            # Sending the response to the client
            response = make_response(data.decode('utf-8'), 200)
            response.headers['Content-Type'] = content_type
            response.headers['Oslc-Core-Version'] = "2.0"

            return response

        except PluginException as pe:
            response_object = {
                'status': 'fail',
                'message': 'Content-Type Incompatible: {}'.format(pe.message)
            }
            return response_object, 400

        except Exception as e:
            response_object = {
                'status': 'fail',
                'message': 'An exception has ocurred: {}'.format(e.message)
            }
            return response_object, 500

    @rm_ns.expect(specification)
    @rm_ns.response(201, 'Specification successfully created.')
    def post(self):
        """
        Insert a Specification to the store converted also in a Requirement

        Use this method to create a new specification item on the store.

        Use the next example as an input


        ```
        {
          "specification_id": "X1C2V3B6",
          "product": "OSLC SDK 6",
          "project": "OSLC-Project 6",
          "title": "OSLC RM Spec 6",
          "description": "The OSLC RM Specification needs to be awesome 6",
          "source": "Ian Altman",
          "author": "Frank",
          "category": "Customer Requirement",
          "discipline": "Software Development",
          "revision": "0",
          "target_value": "1",
          "degree_of_fulfillment": "0",
          "status": "Draft"
        }
        ```
        """

        data = specification_parser.parse_args()
        rq = RQ()
        rq.from_json(data)
        data = rq.to_mapped_object()

        if data:
            path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')

            with open(path, 'rb') as f:
                reader = csv.DictReader(f, delimiter=';')
                field_names = reader.fieldnames

            with open(path, 'a') as f:
                writer = csv.DictWriter(f, fieldnames=field_names, delimiter=';')
                writer.writerow(data)
        else:
            response_object = {
                'status': 'fail',
                'message': 'Not Found'
            }
            return response_object, 400

        return make_response('{}', 201)


@rm_ns.route('/requirement/<string:id>')
class RequirementItem(Resource):

    def get(self, id):
        """
        Retrieve a specific requirement using an ID value

        :param id:
        :return:
        """

        try:
            # Getting the content-type for checking the
            # response we will use to serialize the RDF response.
            content_type = request.headers['accept']
            if content_type in ('application/json-ld', 'application/json'):
                # If the content-type is any kind of json,
                # we will use the json-ld format for the response.
                content_type = 'json-ld'

            # Instantiating the graph where we will store
            # all the requirements from the source (csv file)
            graph = Graph()

            # Loading information from the specification.csv file
            # located on the examples folder of the pyoslc project.
            path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')
            with open(path, 'rb') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    if row['Specification_id'] == id:
                        rq = RQ()               # instantiating the Requirement object
                        rq.update(row)          # Parsing the specification to requirement
                        graph += rq.to_rdf()    # Accumulating the triples on the graph

            # Serializing (converting) each triples of the graph
            # on the selected type for the response
            data = graph.serialize(format=content_type)

            # Sending the response to the client
            response = make_response(data.decode('utf-8'), 200)
            response.headers['Content-Type'] = content_type
            response.headers['Oslc-Core-Version'] = "2.0"

            return response

        except PluginException as pe:
            response_object = {
                'status': 'fail',
                'message': 'Content-Type Incompatible: {}'.format(pe.message)
            }
            return response_object, 400

        except Exception as e:
            response_object = {
                'status': 'fail',
                'message': 'An exception has ocurred: {}'.format(e.message)
            }
            return response_object, 500

    @rm_ns.expect(specification)
    def put(self, id):
        """
        Update the status or information about a Requirement.
        For using this method to update the information for the Requirement
        it will require the ID of the Specification and the new data.

        :param id: The specification ID
        :return:
        """

        data = specification_parser.parse_args()

        if data:
            path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')

            tempfile = NamedTemporaryFile(mode='w', delete=False)

            with open(path, 'rb') as f:
                reader = csv.DictReader(f, delimiter=';')
                field_names = reader.fieldnames

            with open(path, 'r') as csvfile, tempfile:
                reader = csv.DictReader(csvfile, fieldnames=field_names, delimiter=';')
                writer = csv.DictWriter(tempfile, fieldnames=field_names, delimiter=';')
                for row in reader:
                    if row['Specification_id'] == str(id):
                        print('updating row', row['Specification_id'])
                        rq = RQ()
                        rq.from_json(data)
                        row = rq.to_mapped_object()
                        row['Specification_id'] = id
                    writer.writerow(row)

            shutil.move(tempfile.name, path)

        return make_response('{}', 200)

    def delete(self, id):
        """
        Deleting a Requirement
        This method will remove a requirement from the store
        """

        if id:
            path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')

            tempfile = NamedTemporaryFile(mode='w', delete=False)

            with open(path, 'rb') as f:
                reader = csv.DictReader(f, delimiter=';')
                field_names = reader.fieldnames

            with open(path, 'r') as csvfile, tempfile:
                reader = csv.DictReader(csvfile, fieldnames=field_names, delimiter=';')
                writer = csv.DictWriter(tempfile, fieldnames=field_names, delimiter=';')
                for row in reader:
                    if row['Specification_id'] != str(id):
                        writer.writerow(row)

            shutil.move(tempfile.name, path)
            return make_response('{}', 200)
        else:
            return make_response('{Id is required}', 400)


@rm_ns.route('/collection')
class Upload(Resource):

    @api.expect(parsers.csv_file_upload)
    def post(self):
        """
        Load a set of specification

        :param id:
        :return:
        """
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

