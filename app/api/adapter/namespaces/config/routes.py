from urlparse import urlparse

from flask import url_for, request, render_template, make_response
from flask_restx import Namespace
from rdflib.plugin import register
from rdflib.serializer import Serializer

from app.api.adapter.namespaces.core import OslcResource
from app.api.adapter.services.providers import ConfigurationManagementSingleton

config_ns = Namespace(name='config', description='Configuration Management', path='/config')


register(
    'config-xml', Serializer,
    'pyoslc.serializers.configxml', 'ConfigurationSerializer'
)

#
# @config_ns.route('/catalog')
# class ConfigurationCatalog(OslcResource):
#
#     def get(self):
#         endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
#         base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)
#
#         catalog_url = urlparse(base_url).geturl()
#
#         catalog = ConfigurationManagementSingleton.get_catalog(catalog_url)
#
#         # catalog.to_rdf(self.graph)
#
#         response = make_response(render_template('pyoslc_oauth/configuration.html',
#                                                  about=catalog_url,
#                                                  components=catalog_url.replace('catalog', 'components/Component-1')))
#
#         response.headers['max-age'] = '0'
#         response.headers['pragma'] = 'no-cache'
#         response.headers['Cache-Control'] = 'no-cache'
#         response.headers['Content-Length'] = len(response.data)
#         response.headers['Content-Type'] = 'application/rdf+xml;charset=UTF-8'
#         response.headers['OSLC-Core-Version'] = "2.0"
#
#         return response
#
#         # return self.create_response(graph=self.graph, rdf_format="config-xml")
#
#
# @config_ns.route('/components/<string:component_id>')
# class ConfigurationComponent(OslcResource):
#
#     def get(self, component_id):
#         endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint), component_id=component_id)
#         base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)
#
#         components_url = urlparse(base_url).geturl()
#
#         provider = ConfigurationManagementSingleton.get_component(components_url, component_id)
#         # provider.to_rdf(self.graph, config=True)
#
#         response = make_response(render_template('pyoslc_oauth/components.html',
#                                                  dialog=provider.about))
#
#         response.headers['max-age'] = '0'
#         response.headers['pragma'] = 'no-cache'
#         response.headers['Cache-Control'] = 'no-cache'
#         response.headers['Content-Length'] = len(response.data)
#         response.headers['Content-Type'] = 'application/rdf+xml;charset=UTF-8'
#         response.headers['OSLC-Core-Version'] = "2.0"
#
#         return response
#         # return self.create_response(graph=self.graph, rdf_format="config-xml")
#
#
# @config_ns.route('/publisher')
# class ConfigurationPublisher(OslcResource):
#
#     def get(self):
#         endpoint_url = url_for('{}.{}'.format(request.blueprint, self.endpoint))
#         base_url = '{}{}'.format(request.url_root.rstrip('/'), endpoint_url)
#
#         components_url = urlparse(base_url).geturl()
#
#         # provider = ConfigurationManagementSingleton.get_component(components_url)
#         # provider.to_rdf(self.graph, config=True)
#
#         response = make_response(render_template('pyoslc_oauth/publisher.html',
#                                                  dialog=components_url))
#
#         response.headers['max-age'] = '0'
#         response.headers['pragma'] = 'no-cache'
#         response.headers['Cache-Control'] = 'no-cache'
#         response.headers['Content-Length'] = len(response.data)
#         response.headers['Content-Type'] = 'application/rdf+xml;charset=UTF-8'
#         response.headers['OSLC-Core-Version'] = "2.0"
#
#         return response
#         # return self.create_response(graph=self.graph, rdf_format="config-xml")
