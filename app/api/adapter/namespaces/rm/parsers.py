from flask_restx import reqparse
from werkzeug.datastructures import FileStorage

csv_file_upload = reqparse.RequestParser()
csv_file_upload.add_argument('csv_file', type=FileStorage, location='files', required=True, help='CSV File')


specification_parser = reqparse.RequestParser()
specification_parser.add_argument('specification_id', type=str, required=True, help='ID of the specification')
specification_parser.add_argument('product', type=str, required=True, help='Name of the product')
specification_parser.add_argument('project', type=str, required=True, help='Name of the project')
specification_parser.add_argument('title', type=str, required=True, help='Title of the specification')
specification_parser.add_argument('description', type=str, required=True, help='Description of the specification')
specification_parser.add_argument('source', type=str, required=True, help='Source of the specification')
specification_parser.add_argument('author', type=str, required=True, help='Author of the specification')
specification_parser.add_argument('category', type=str, required=True, help='Category of the specification')
specification_parser.add_argument('discipline', type=str, required=True, help='Discipline of th specification')
specification_parser.add_argument('revision', type=str, required=True, help='Revision')
specification_parser.add_argument('target_value', type=str, required=True, help='Target value of the specification')
specification_parser.add_argument('degree_of_fulfillment', type=str, required=True, help='Degree of fulfillment of the specification')
specification_parser.add_argument('status', type=str, required=True, help='Status of the specification')

specification_id_parser = reqparse.RequestParser()
specification_id_parser.add_argument('id', type=str, help='ID of the specification')
