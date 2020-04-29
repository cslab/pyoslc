from flask_restplus import Namespace

from webservice.api.oslc import api
from webservice.api.oslc.rm.endpoints import RequirementList, RequirementItem, UploadCollection
from webservice.api.oslc.rm.endpoints_v2 import QueryCapability

rm_ns = Namespace(name='rm', description='Requirements Management', path='/rm')

rm_ns.add_resource(RequirementList, "/requirement")
rm_ns.add_resource(RequirementItem, "/requirement/<string:id>")
# rm_ns.add_resource(UploadCollection, "/collection")
# rm_ns.add_resource(QueryCapability, "/query_capability", defaults={'query_capability_id': ''})

api.add_namespace(rm_ns)
