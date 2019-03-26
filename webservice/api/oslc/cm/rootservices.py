from flask import make_response
from flask_restplus import Resource


class RootServices(Resource):

    def get(self):
        return make_response('{}', 200)
