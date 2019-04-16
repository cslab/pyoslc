from flask_restplus import Namespace

from webservice.api.oslc import api
from webservice.api.oslc.rm.endpoints import QueryCapability

rm_ns = Namespace(name='rm', description='Requirements Management', path='/rm')

rm_ns.add_resource(QueryCapability, "/query_capability")

api.add_namespace(rm_ns)
