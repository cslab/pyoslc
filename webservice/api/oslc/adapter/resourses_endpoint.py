# from webservice.api.oslc.adapter.endpoints import OSLCResource
#
#
# class ResourceShape(OSLCResource):
#
#     def __init__(self, api=None, *args, **kwargs):
#         super(ResourceShape, self).__init__(api, *args, **kwargs)
#         self.graph = kwargs['graph']
#         self.catalog = kwargs['catalog']
#
#     def get(self, service_provider_id):
#         service_provider = next((sp for sp in self.catalog.service_provider if sp.identifier == service_provider_id),
#                                 None)
#
#         if service_provider:
#             self.service_provider.to_rdf(self.graph)
#             # for sp in self.graph[OSLCCore.ServiceProvider]:
#             #     for s in sp[OSLCCore.service]:
#             #         print(s)
#             return self.create_response(self.graph)
#
#         # return None
