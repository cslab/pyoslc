from __future__ import absolute_import
from __future__ import division

import json
import logging
import os

import six

from .logging import default_handler

if six.PY3:
    from urllib.parse import parse_qsl, unquote
else:
    from urlparse import parse_qsl, unquote

from math import ceil
from xml.sax import SAXParseException

from rdflib import Graph
from six import text_type
from six.moves.urllib.parse import urlparse
from werkzeug.exceptions import (
    UnsupportedMediaType,
    BadRequest,
    NotImplemented,
    NotFound,
)

from pyoslc.resources.query import Criteria
from pyoslc_server import request

from pyoslc.resources.models import ResponseInfo, BaseResource, Compact, Preview

from .resource import OSLCResource
from .providers import ServiceProviderCatalogSingleton
from .helpers import url_for, make_response
from .utils import get_url
from .wrappers import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(default_handler)


class ServiceProviderCatalog(OSLCResource):
    def __init__(self, *args, **kwargs):
        super(ServiceProviderCatalog, self).__init__(*args, **kwargs)
        self.title = kwargs.get("title", None)
        self.description = kwargs.get("description", None)
        adapter = kwargs.get("adapter", None)
        if adapter and not (adapter in self.adapters):
            self.adapters.append(adapter)

    def get(self):
        super(ServiceProviderCatalog, self).get()
        endpoint_url = url_for("{}".format(request.endpoint))
        base_url = "{}{}".format(request.url_root.rstrip("/"), endpoint_url)

        catalog_url = urlparse(base_url).geturl()

        catalog = ServiceProviderCatalogSingleton.get_catalog(
            catalog_url,
            self.title,
            self.description,
            self.api.default_namespace.adapters,
        )
        catalog.to_rdf(self.graph)

        return self.create_response(graph=self.graph)


class ServiceProvider(OSLCResource):
    def __init__(self, *args, **kwargs):
        super(ServiceProvider, self).__init__(*args, **kwargs)
        self.title = kwargs.get("title", None)
        self.description = kwargs.get("description", None)
        self.providers = kwargs.get("providers", None)

    def get(self, provider_id):
        super(ServiceProvider, self).get()
        endpoint_url = url_for("{}".format(self.endpoint), provider_id=provider_id)
        base_url = "{}{}".format(request.url_root.rstrip("/"), endpoint_url)

        service_provider_url = urlparse(base_url).geturl()

        provider = ServiceProviderCatalogSingleton.get_provider(
            service_provider_url,
            provider_id,
            adapters=self.api.default_namespace.adapters,
        )
        if not provider:
            raise NotFound(
                "The Service Provider with ID {}, was not found.".format(provider_id)
            )

        provider.to_rdf(self.graph)
        return self.create_response(graph=self.graph)


class ResourceListOperation(OSLCResource):
    def get(self, provider_id):
        super(ResourceListOperation, self).get()

        qs = request.args

        paging = qs.get("oslc.paging", False)
        if isinstance(paging, text_type):
            paging = eval(paging.capitalize())

        page_size = qs.get("oslc.pageSize", 0)
        page_no = qs.get("oslc.pageNo", 0)
        prefix = qs.get("oslc.prefix", "")
        where = qs.get("oslc.where", "")
        select = qs.get("oslc.select", "")

        pfx = ["{}=<{}>".format(ns[0], ns[1]) for ns in self.graph.namespaces()]
        pfx = ", ".join(pfx)
        prefix += ", " + pfx
        # prefix += [{prefix, ns.toPython()} for prefix, ns in self.graph.namespace_manager.namespaces()]

        criteria = Criteria()
        criteria.prefix(prefix)
        criteria.where(where)
        criteria.select(select)

        endpoint_url = url_for("{}".format(self.endpoint), provider_id=provider_id)
        base_url = "{}{}".format(request.url_root.rstrip("/"), endpoint_url)
        base_url_with_query = base_url

        provider = ServiceProviderCatalogSingleton.get_provider(
            base_url, provider_id, adapters=self.api.default_namespace.adapters
        )
        if not provider:
            raise NotFound(
                "The Service Provider with ID {}, was not found.".format(provider_id)
            )

        request.view_args.pop("provider_id")

        next_url = ""
        paging = paging if paging else int(page_size) > 0
        if paging:
            page_size = int(page_size) if int(page_size) else 50
            page_no = int(page_no) if int(page_no) else 1

            params = {"oslc.paging": "true"}
            if page_size:
                params["oslc.pageSize"] = int(page_size)

            if page_no:
                params["oslc.pageNo"] = int(page_no)

            base_url_with_query = get_url(base_url, params)

        data = None
        total_count = 0
        adapter = self.get_adapter(provider_id)
        if adapter:
            adapter.namespaces = criteria.prefixes
            total_count, data = adapter.query_capability(
                paging=paging,
                page_size=page_size,
                page_no=page_no,
                prefix=criteria.prefixes,
                where=criteria.conditions,
                select=criteria.properties,
                **request.view_args
            )
            logger.debug(
                "{} QueryCapability returns: <total_count: {}> - <len(data): {}>".format(
                    adapter.identifier, total_count, len(data)
                )
            )

            result = list()
            for item in data:
                br = BaseResource()
                br.update(item, adapter, base_url)
                br.about = br.get_absolute_url(
                    base_url=base_url, identifier=br.identifier
                )
                for t in adapter.types:
                    br.types.append(t)
                result.append(br)
            data = result

            logger.debug("QueryCapability: <pageSize: {}>".format(page_size))
            if page_size:
                pages = ceil(total_count / page_size)
                logger.debug("QueryCapability: <pages: {}>".format(pages))
                if int(page_no) < pages:
                    params["oslc.pageNo"] = int(page_no) + 1
                    next_url = get_url(base_url_with_query, params)

        if not data:
            raise NotFound("No resources from provider with ID {}".format(provider_id))

        response_info = ResponseInfo(base_url)
        response_info.total_count = total_count
        response_info.title = "Query Results for Requirements"

        response_info.members = data
        response_info.current_page = base_url_with_query
        response_info.next_page = next_url

        # Create a list of elements directly when not using the Paging
        response_info.to_rdf(
            self.graph, base_url=base_url, attributes=adapter, criteria=criteria
        )

        return self.create_response(graph=self.graph)

    def post(self, provider_id):

        if request.accept_mimetypes.best and not (
            request.accept_mimetypes.best in ("*/*", "text/html")
        ):
            accept = request.accept_mimetypes.best

        if not (
            accept
            in (
                "text/turtle",
                "application/rdf+xml",
                "application/ld+json",
                "application/xml",
                "application/atom+xml",
            )
        ):
            raise UnsupportedMediaType

        endpoint_url = url_for("{}".format(self.endpoint), provider_id=provider_id)
        base_url = "{}{}".format(request.url_root.rstrip("/"), endpoint_url)

        provider = ServiceProviderCatalogSingleton.get_provider(
            base_url, provider_id, adapters=self.api.default_namespace.adapters
        )
        if not provider:
            raise NotFound(
                "The Service Provider with ID {}, was not found.".format(provider_id)
            )

        if accept == "application/json":
            # data = specification_parser.parse_args()
            pass
        else:
            try:
                data = Graph().parse(data=request.data, format="xml")
                adapter = self.get_adapter(provider_id)
                if adapter:

                    pfx = [
                        "{}=<{}>".format(ns[0], ns[1]) for ns in self.graph.namespaces()
                    ]
                    pfx = ", ".join(pfx)
                    criteria = Criteria()
                    criteria.prefix(pfx)
                    adapter.namespaces = criteria.prefixes

                    req = BaseResource()
                    req.from_rdf(data, adapter.types[0], attributes=adapter)

                    adapter.creation_factory(req.get_dict(attributes=adapter.mapping))
                    if isinstance(req, BaseResource):
                        req.to_rdf_base(
                            self.graph,
                            base_url=base_url,
                            oslc_types=adapter.types,
                            attributes=adapter,
                        )
                        data = self.graph.serialize(format="turtle")

                        # Sending the response to the client
                        response = Response(
                            data.decode("utf-8") if not isinstance(data, str) else data,
                            201,
                        )
                        response.headers[
                            "Content-Type"
                        ] = request.content_type  # 'application/rdf+xml; charset=UTF-8'
                        response.headers["OSLC-Core-Version"] = "2.0"
                        response.headers["Location"] = base_url + "/" + req.identifier
                        response.set_etag(req.digestion())
                        # response.headers['Last-Modified'] = http_date(datetime.now())

                        return response
                    else:
                        return make_response(req.description, req.code)

            except SAXParseException:
                raise BadRequest()


class ResourceItemOperation(OSLCResource):
    def get(self, provider_id, resource_id):
        super(ResourceItemOperation, self).get()

        accept = request.headers["accept"]

        endpoint_url = url_for(
            "{}".format(self.endpoint), provider_id=provider_id, resource_id=resource_id
        )
        base_url = "{}{}".format(request.url_root.rstrip("/"), endpoint_url)
        service_provider_url = urlparse(base_url).geturl()

        provider = ServiceProviderCatalogSingleton.get_provider(
            service_provider_url,
            provider_id,
            adapters=self.api.default_namespace.adapters,
        )
        if provider:
            try:
                request.view_args.pop("provider_id")

                data = None
                adapter = self.get_adapter(provider_id)
                if adapter:
                    data = adapter.get_resource(**request.view_args)

                # data = self.api.app.adapter_functions[rule.endpoint]('get_resource', **request.view_args)
                resource = BaseResource()
                if data:
                    resource.about = base_url
                    resource.update(data, adapter)
                    resource.to_rdf_base(self.graph, base_url, adapter.types, adapter)

                if (
                    "application/x-oslc-compact+xml" in accept
                    or ", application/x-jazz-compact-rendering" in accept
                ):
                    compact = Compact(about=base_url)
                    compact.title = resource.identifier if resource else "REQ Not Found"
                    compact.icon = url_for(
                        "oslc.static", filename="pyicon24.ico", _external=True
                    )

                    small_preview = Preview()
                    small_preview.document = base_url + "/smallPreview"
                    small_preview.hint_width = "45em"
                    small_preview.hint_height = "10em"

                    large_preview = Preview()
                    large_preview.document = base_url + "/largePreview"
                    large_preview.hint_width = "45em"
                    large_preview.hint_height = "20em"

                    compact.small_preview = small_preview
                    compact.large_preview = large_preview

                    compact.to_rdf(self.graph)

                    accept = "application/x-oslc-compact+xml"
                    rdf_format = "pretty-xml"
                else:
                    # accept = 'text/turtle'
                    rdf_format = "turtle"
                    if accept in ("application/rdf+xml"):
                        rdf_format = "xml"

                return self.create_response(
                    graph=self.graph, accept=accept, rdf_format=rdf_format, etag=True
                )
            except AssertionError as e:
                return NotImplemented(e)

        else:
            raise NotFound(
                "The Service Provider with ID {}, was not found.".format(provider_id)
            )
