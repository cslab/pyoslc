from flask_restx import Namespace

from app.api.adapter.namespaces.rm.routes import RequirementList, RequirementItem

rm_ns = Namespace(name='rm', description='Requirements Management', path='/rm')

rm_ns.add_resource(RequirementList, "/artifact/requirement")
rm_ns.add_resource(RequirementItem, "/artifact/requirement/<string:id>")
# rm_ns.add_resource(UploadCollection, "/collection")
# rm_ns.add_resource(QueryCapability, "/query_capability", defaults={'query_capability_id': ''})
