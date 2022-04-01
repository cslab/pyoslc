from __future__ import absolute_import

import logging

from rdflib import Graph, RDF, RDFS, DCTERMS
from rdflib.plugin import PluginException
from werkzeug.exceptions import UnsupportedMediaType

from pyoslc.vocabularies.core import OSLC
from pyoslc_server import request

from .views import OSLCResourceView
from .wrappers import Response

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class OSLCResource(OSLCResourceView):

    title = ""
    description = ""
    adapters = list()

    def __init__(self, *args, **kwargs):
        super(OSLCResource, self).__init__(*args, **kwargs)

        self.graph = kwargs.get("graph", Graph())
        self.graph.bind("oslc", OSLC)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("dcterms", DCTERMS)
        # self.graph.bind('j.0', JAZZ_PROCESS)
        # prefix_definitions.append(PrefixDefinition(prefix='dcterms', prefix_base=DCTERMS))
        # prefix_definitions.append(PrefixDefinition(prefix='oslc', prefix_base=OSLC))
        # prefix_definitions.append(PrefixDefinition(prefix='oslc_data', prefix_base=OSLCData))
        # prefix_definitions.append(PrefixDefinition(prefix='rdf', prefix_base=RDF))
        # prefix_definitions.append(PrefixDefinition(prefix='rdfs', prefix_base=RDFS))
        # prefix_definitions.append(PrefixDefinition(prefix='oslc_am', prefix_base=OSLC_AM))
        # prefix_definitions.append(PrefixDefinition(prefix='oslc_cm', prefix_base=OSLC_CM))
        # prefix_definitions.append(PrefixDefinition(prefix='oslc_rm', prefix_base=OSLC_RM))

    def get(self, *args, **kwargs):
        accept = request.headers.get("accept")
        logger.debug("accept: {}".format(accept))

        if accept in ("*/*", "text/html"):
            accept = "text/turtle"

        if not (
            accept
            in (
                "application/rdf+xml",
                "application/json",
                "application/ld+json",
                "application/json-ld",
                "application/xml",
                "application/atom+xml",
                "text/turtle",
                "application/xml, application/x-oslc-cm-service-description+xml",
                "application/x-oslc-compact+xml, application/x-jazz-compact-rendering; q=0.5",
                "application/rdf+xml,application/x-turtle,application/ntriples,application/json",
            )
        ):
            print("unsupported media type")
            raise UnsupportedMediaType

    @staticmethod
    def create_response(graph, accept=None, content=None, rdf_format=None, etag=False):

        # Getting the content-type for checking the
        # response we will use to serialize the RDF response.
        accept = (
            accept
            if accept is not None
            else request.headers.get("accept", "application/rdf+xml")
        )
        if accept in ("*/*", "text/html"):
            accept = "text/turtle"

        content = (
            content
            if content is not None
            else request.headers.get("content-type", accept)
        )
        if content.__contains__("x-www-form-urlencoded") or content.__contains__(
            "text/plain"
        ):
            content = accept

        rdf_format = accept if rdf_format is None else rdf_format

        if accept in ("application/json-ld", "application/ld+json", "application/json"):
            # If the content-type is any kind of json,
            # we will use the json-ld format for the response.
            rdf_format = "json-ld"

        # if rdf_format in 'config-xml':
        #     rdf_format = 'config-xml'
        # else:
        #     rdf_format = 'pretty-xml'

        if rdf_format in ("application/xml", "application/rdf+xml"):
            rdf_format = "pretty-xml"

        if rdf_format.__contains__("rootservices-xml") and (
            not accept.__contains__("xml")
        ):
            rdf_format = accept

        if rdf_format == "application/atom+xml":
            rdf_format = "pretty-xml"

        if rdf_format in (
            "application/xml, application/x-oslc-cm-service-description+xml"
        ):
            rdf_format = "pretty-xml"
            content = "application/rdf+xml"

        try:
            logger.debug("Parsing the Graph into {}".format(rdf_format))
            data = graph.serialize(format=rdf_format)
        except PluginException as pe:
            response_object = {
                "status": "fail",
                "message": "Content-Type Incompatible: {}".format(pe),
            }
            return response_object, 400

        # Sending the response to the client
        response = Response(
            data.decode("utf-8") if not isinstance(data, str) else data, 200
        )
        response.headers["Accept"] = accept
        response.headers["Content-Type"] = content
        response.headers["OSLC-Core-Version"] = "2.0"

        if etag:
            response.add_etag()

        return response

    def get_adapter(self, identifier):
        _adapters = [
            adapter
            for adapter in self.api.default_namespace.adapters
            if adapter.identifier == identifier
        ]
        if _adapters:
            return _adapters[0]
