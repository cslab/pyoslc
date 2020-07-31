import csv
import os
import shutil
from tempfile import NamedTemporaryFile

from flask import make_response, request, render_template, current_app
from flask_restplus import Resource
from rdflib import Graph, RDF
from rdflib.plugin import PluginException

from pyoslc.resources.domains.rm import Requirement
from pyoslc.vocabulary.rm import OSLC_RM
from webservice.api.oslc import api
from webservice.api.oslc.adapter.mappings.specification import specification_map
from webservice.api.oslc.rm import parsers
from webservice.api.oslc.rm.models import specification
from webservice.api.oslc.rm.parsers import specification_parser

attributes = specification_map


@api.representation('application/rdf+xml')
@api.representation('application/json-ld')
@api.representation('text/turtle')
class RequirementList(Resource):
    """
    Class for implementing the methods to manage
    the specification/requirement items, for retrieving,
    the list of items or inserting an item.
    """

    @api.response(200, 'The RDF formatted response of the requirements, taken from the specification')
    def get(self):
        """
        Returns the list of Requirements converted from the Specification
        Listing the Specification statements on the RDF format using the RM domain
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
                    req = Requirement()      # instantiating the Requirement object
                    req.update(row, attributes)          # Parsing the specification to requirement
                    graph += req.to_rdf(request.base_url, attributes)    # Accumulating the triples on the graph

            if 'text/html' in content_type:
                # Validating whether the request comes from
                # a web browser or a human readeble client
                # if so, then return the list to the template
                requirements = list()
                for r in graph.subjects(RDF.type, OSLC_RM.Requirement):
                    requirements.append(r)

                response = make_response(render_template('web/requirement_list.html',
                                                         requirements=requirements), 200)
            else:
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

    @api.expect(specification)
    @api.response(201, 'Specification successfully created.')
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
        content_type = request.headers['content-type']
        if content_type != 'application/rdf+xml':
            data = specification_parser.parse_args()
        else:
            print('TODO - transform from rdf')

        req = Requirement()
        req.from_json(data, attributes)
        data = req.to_mapped_object()

        if data:
            path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')

            tempfile = NamedTemporaryFile(mode='w', delete=False)

            with open(path, 'rb') as f:
                reader = csv.DictReader(f, delimiter=';')
                field_names = reader.fieldnames

            with open(path, 'r') as csvfile, tempfile:
                reader = csv.DictReader(csvfile, fieldnames=field_names, delimiter=';')
                writer = csv.DictWriter(tempfile, fieldnames=field_names, delimiter=';')
                exist = False
                for row in reader:
                    if row['Specification_id'] == data['Specification_id']:
                        exist = True
                    writer.writerow(row)

                if not exist:
                    writer.writerow(data)

            shutil.move(tempfile.name, path)

            if exist:
                response_object = {
                    'status': 'fail',
                    'message': 'Not Modified'
                }
                return response_object, 304

        else:
            response_object = {
                'status': 'fail',
                'message': 'Not Found'
            }
            return response_object, 400

        return make_response(req.about, 201)


class RequirementItem(Resource):
    """
    Class for implementing the methods to manage
    the specification/requirement items, for retrieving,
    updating or deleting items specified by the parameter
    """

    def get(self, id):
        """
        Retrieve a specific requirement using an ID value

        Use this method to get the information which describes
        the requirement/specification
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
                        rq = Requirement()               # instantiating the Requirement object
                        rq.update(row, attributes)          # Parsing the specification to requirement
                        graph += rq.to_rdf(request.base_url, attributes)    # Accumulating the triples on the graph

            if 'text/html' in content_type:
                # Passing the graph as a parameter to the template
                # for going through the data and showing the information
                response = make_response(render_template('web/requirement.html', id=id, statements=graph), 200)
            else:
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

    @api.expect(specification)
    def put(self, id):
        """
        Update the status or information about a Requirement.
        For using this method to update the information for the Requirement
        it will require the ID of the Specification and the new data.
        """
        data = specification_parser.parse_args()

        if data:
            path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')

            tempfile = NamedTemporaryFile(mode='w', delete=False)

            with open(path, 'rb') as f:
                reader = csv.DictReader(f, delimiter=';')
                field_names = reader.fieldnames

            modified = False
            with open(path, 'r') as csvfile, tempfile:
                reader = csv.DictReader(csvfile, fieldnames=field_names, delimiter=';')
                writer = csv.DictWriter(tempfile, fieldnames=field_names, delimiter=';')
                for row in reader:
                    if row['Specification_id'] == str(id):
                        rq = Requirement()
                        rq.from_json(data)
                        row = rq.to_mapped_object()
                        row['Specification_id'] = id
                        modified = True
                    writer.writerow(row)

            shutil.move(tempfile.name, path)

            if not modified:
                return make_response('{Not Modified}', 304)

        return make_response('{}', 200)

    def delete(self, id):
        """
        Deleting a Requirement
        This method will remove a requirement from the store
        """

        path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')

        tempfile = NamedTemporaryFile(mode='w', delete=False)

        with open(path, 'rb') as f:
            reader = csv.DictReader(f, delimiter=';')
            field_names = reader.fieldnames

        modified = False
        with open(path, 'r') as csvfile, tempfile:
            reader = csv.DictReader(csvfile, fieldnames=field_names, delimiter=';')
            writer = csv.DictWriter(tempfile, fieldnames=field_names, delimiter=';')
            for row in reader:
                if row['Specification_id'] != str(id):
                    writer.writerow(row)
                else:
                    modified = True

        shutil.move(tempfile.name, path)

        if not modified:
            return make_response('{Not Modified}', 304)

        return make_response('{}', 200)


class UploadCollection(Resource):
    """
    Class for implementing the method for uploading
    data to the store
    """

    @api.expect(parsers.csv_file_upload)
    def post(self):
        """
        Load a set of specification from a CSV file
        Use this method for uploading a collection of specifications
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
            return make_response('{Bad request}', 404)

        return make_response('{\'status\': \'Done\'}', 200)
