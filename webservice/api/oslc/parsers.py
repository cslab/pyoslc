from flask_restplus import reqparse
from werkzeug.datastructures import FileStorage

csv_file_upload = reqparse.RequestParser()
csv_file_upload.add_argument('csv_file', type=FileStorage, location='files', required=True, help='CSV File')
