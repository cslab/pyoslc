import six

if six.PY3:
    from urllib.parse import urlparse, parse_qsl, unquote,  quote
else:
    from urllib import quote
    from urlparse import urlparse, parse_qsl, unquote

from rdflib import Graph, RDF, URIRef, DCTERMS, Literal, RDFS

from pyoslc.vocabularies.core import OSLC
from pyoslc.vocabularies.rm import OSLC_RM


def test_not_found(pyoslc_enabled):
    """
    GIVEN the PyOSLC API and an invalid URL
    WHEN requesting the URL for getting the reponse
    THEN
        validating the status code of the response which should be BAD REQUEST (400)
    """

    response = pyoslc_enabled.get_url("/oslc")

    assert response is not None
    assert response.status_code == 404

    g = Graph()
    g.parse(data=response.data, format="text/turtle")

    assert g is not None, "The response should be a RDF Graph"

    assert (
        g.subjects(RDF.type, OSLC.Error) is not None
    ), "The Error should be on the response"


def test_unsupported_media_type(pyoslc_enabled):
    """
    GIVEN the PyOSLC API and an invalid RDF representation
    WHEN requesting the catalog endpoint for getting the ServiceProviderCatalog
    THEN
        validating the status code of the response which should be BAD REQUEST (415)
    """

    representation = "jsonld"

    response = pyoslc_enabled.get_catalog(representation)

    assert response is not None
    assert response.status_code == 415

    g = Graph()
    g.parse(data=response.data, format="text/turtle")

    assert g is not None, "The response should be a RDF Graph"

    subject = URIRef("http://localhost/oslc/services/catalog")

    assert (subject, RDF.type, OSLC.Error) in g, "The Error was not generated"
    assert (
        subject,
        OSLC.statusCode,
        Literal(415),
    ) in g, "The status code it should be 415"


def test_service_provider_catalog(pyoslc_enabled):
    """
    GIVEN the PyOSLC API and a list of RDF representations
    WHEN requesting the catalog endpoint for getting the ServiceProviderCatalog
    THEN
        validating the status code of the response
        parsing the response content into a graph in the rdf representation format
        validating whether the ServiceProviderCatalog statement is within the graph
    """

    representations = ["application/rdf+xml", "application/json-ld", "text/turtle"]

    for representation in representations:

        response = pyoslc_enabled.get_catalog(representation)
        assert response is not None
        assert response.status_code == 200

        g = Graph()
        g.parse(
            data=response.data,
            format=representation
            if representation != "application/json-ld"
            else "json-ld",
        )

        assert g is not None, "The response should be an RDF Graph"

        spc = URIRef("http://localhost/oslc/services/catalog")
        url = "http://localhost/oslc/services/provider/{provider_id}".format(
            provider_id="adapter"
        )
        sp = URIRef(url)

        assert (
            spc,
            RDF.type,
            OSLC.ServiceProviderCatalog,
        ) in g, "The ServiceProviderCatalog was not generated"
        assert sp in g.objects(), "The ServiceProvider URI is not in the graph"
        assert (
            spc,
            OSLC.serviceProvider,
            None,
        ) in g, "The response does not contain a ServiceProvider"
        assert (
            spc,
            OSLC.domain,
            URIRef(OSLC_RM.uri) if isinstance(OSLC_RM.uri, str) else OSLC_RM.uri,
        ) in g, "The ServiceProvider is not on RM domain"

        assert (
            "Service Provider Catalog" in [t for t in g.objects(spc, DCTERMS.title)][0]
        )
        assert sp in [t for t in g.objects(spc, OSLC.serviceProvider)]


def test_bad_service_provider(pyoslc_enabled):
    """
    GIVEN the PyOSLC API
    WHEN requesting the service provider endpoint for getting the ServiceProvider
         with a non existent id
    THEN
        validating the status code of the response that should be 404
    """

    response = pyoslc_enabled.get_service_provider("Project-1a")
    assert response is not None
    assert response.status_code == 404
    assert b"The Service Provider with ID Project-1a, was not found." in response.data

    g = Graph()
    g.parse(data=response.data, format="application/rdf+xml")

    assert g is not None, "The response should be an RDF Graph"

    subject = URIRef("http://localhost/oslc/services/provider/Project-1a")

    assert (subject, RDF.type, OSLC.Error) in g, "The Error was not generated"
    assert (
        subject,
        OSLC.statusCode,
        Literal(404),
    ) in g, "The status code it should be 404"
    if six.PY3:
        message = str(next(g.objects(subject, OSLC.message)))
    else:
        message = str(g.objects(subject, OSLC.message).next())
    assert message.__contains__(
        "Project-1a"
    ), "The message should contain the project id"


def test_service_provider(pyoslc_enabled):
    """
    GIVEN the PyOSLC API
    WHEN requesting the service provider endpoint for getting the ServiceProvider
         with a specific id
    THEN
        validating the status code of the response
        parsing the response content into a graph in the application/rdf+xml format
        validating whether the ServiceProviderCatalog statement is not within the graph
        validating that the ServiceProvider is within the graph
        validating the attributes for the integration with a global configuration project
    """

    provider_id = "adapter"

    response = pyoslc_enabled.get_service_provider(provider_id)
    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format="application/rdf+xml")

    assert g is not None

    url = "http://localhost/oslc/services/provider/{provider_id}".format(
        provider_id=provider_id
    )
    sp = URIRef(url)

    assert (
        None,
        RDF.type,
        OSLC.ServiceProviderCatalog,
    ) not in g, "The ServiceProviderCatalog should not be generated"
    assert (
        sp,
        RDF.type,
        OSLC.ServiceProvider,
    ) in g, "The ServiceProvider was not generated"
    assert sp in g.subjects(), "The ServiceProvider URI is not in the graph"
    assert (sp, OSLC.service, None) in g, "The response does not contain a Service"
    assert (
        sp,
        DCTERMS.identifier,
        None,
    ) in g, "The ServiceProvider should have a identifier"

    assert provider_id in [t for t in g.objects(sp, DCTERMS.identifier)][0]


def test_query_capability_basic(pyoslc_enabled):
    """
    GIVEN the PyOSLC API
    WHEN requesting the query capability endpoint for getting the
         list of Requirements with a specific project id
    THEN
        validating the status code of the response
        parsing the response content into a graph in the application/rdf+xml format
        validating whether the ResponseInfo statement is within the graph
        validating that the member attribute is present on the graph
        validating that at least the first three records from the csv file are present
    """

    response = pyoslc_enabled.get_query_capability("adapter")
    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format="application/rdf+xml")

    assert g is not None

    ri = URIRef("http://localhost/oslc/services/provider/adapter/resources")

    assert (
        not (None, RDF.type, OSLC.ResponseInfo) in g
    ), "The ResponseInfo was generated and should not"

    assert (ri, RDFS.member, None) in g, "The response does not contain a member"
    assert (
        not (ri, OSLC.totalCount, None) in g
    ), "The response contains the totalCount and should not"
    assert (
        not (ri, DCTERMS.title, None) in g
    ), "The ResponseInfo should not be part of the response"

    members = [m for m in g.objects(ri, RDFS.member)]
    assert members is not None, "The ResponseInfo should have members"
    assert len(members) == 5, "The members should contain at least one element"


def test_query_capability_paging(pyoslc_enabled):
    response = pyoslc_enabled.get_query_capability("adapter", paging=True, page_size=2)

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format="application/rdf+xml")

    assert g is not None

    ri = URIRef("http://localhost/oslc/services/provider/adapter/resources")

    assert (
        None,
        RDF.type,
        OSLC.ResponseInfo,
    ) in g, "The ResponseInfo should be generated"

    ril = [a for a in g.subjects(RDF.type, OSLC.ResponseInfo)][0]

    assert (ri, RDFS.member, None) in g, "The response does not contain a member"
    assert (
        ril,
        OSLC.totalCount,
        None,
    ) in g, "The response does not contain the totalCount"
    assert (
        int([o for o in g.objects(ril, OSLC.totalCount)][0]) == 5
    ), "The response does not contain the totalCount"
    assert (ril, DCTERMS.title, None) in g, "The ResponseInfo should have a title"
    assert (
        ril,
        OSLC.nextPage,
        None,
    ) in g, "The ResponseInfo should have a nextPage attribute"

    members = [m for m in g.objects(ri, RDFS.member)]
    assert members is not None, "The ResponseInfo should have members"
    assert len(members) == 2, "The members should contain at least one element"


def test_query_capability_next_page(pyoslc_enabled):
    response = pyoslc_enabled.get_query_capability(
        "adapter", paging=True, page_size=2, page_number=2
    )

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format="application/rdf+xml")

    assert g is not None

    ri = URIRef("http://localhost/oslc/services/provider/adapter/resources")

    assert (
        None,
        RDF.type,
        OSLC.ResponseInfo,
    ) in g, "The ResponseInfo should be generated"

    ril = [a for a in g.subjects(RDF.type, OSLC.ResponseInfo)][0]

    assert (ri, RDFS.member, None) in g, "The response does not contain a member"
    assert (
        ril,
        OSLC.totalCount,
        None,
    ) in g, "The response does not contain the totalCount"
    assert (
        int([o for o in g.objects(ril, OSLC.totalCount)][0]) == 5
    ), "The response does not contain the totalCount"

    members = [m for m in g.objects(ri, RDFS.member)]
    assert members is not None, "The ResponseInfo should have members"
    assert len(members) == 2, "The members should contain at least one element"

    r3 = URIRef("http://localhost/oslc/services/provider/adapter/resources/3")
    r4 = URIRef("http://localhost/oslc/services/provider/adapter/resources/4")

    assert r3 in members, "The first resource does not correspond in the response"
    assert r4 in members, "The second resource does not correspond in the response"

    np = [a for a in g.objects(ril, OSLC.nextPage)][0]

    url = urlparse(unquote(np))
    qs = dict(parse_qsl(url.query.replace("&amp;", "&")))

    paging = qs.get("oslc.paging", 0)
    page_size = qs.get("oslc.pageSize", 0)
    page_no = qs.get("oslc.pageNo", 0)

    res = pyoslc_enabled.get_query_capability(
        "adapter", paging=paging, page_size=page_size, page_number=page_no
    )

    assert res is not None
    assert res.status_code == 200

    g = Graph()
    g.parse(data=res.data, format="application/rdf+xml")

    ri = URIRef("http://localhost/oslc/services/provider/adapter/resources")
    ril = [a for a in g.subjects(RDF.type, OSLC.ResponseInfo)][0]

    assert (ri, RDFS.member, None) in g, "The response does not contain a member"
    assert (
        ril,
        OSLC.totalCount,
        None,
    ) in g, "The response does not contain the totalCount"
    assert (
        int([o for o in g.objects(ril, OSLC.totalCount)][0]) == 5
    ), "The response does not contain the totalCount"

    members = [m for m in g.objects(ri, RDFS.member)]
    assert members is not None, "The ResponseInfo should have members"
    assert len(members) == 1, "The members should contain at least one element"

    r5 = URIRef("http://localhost/oslc/services/provider/adapter/resources/5")

    assert r5 in members, "The first resource does not correspond in the response"

    # np = [o for o in g.objects(ril, OSLC.nextPage)]
    # assert len(np) == 0, 'The response should not have a next_page'
    assert (
        not (ril, OSLC.nextPage, None) in g
    ), "The response should not have a next_page"


def test_query_capability_select(pyoslc_enabled):
    response = pyoslc_enabled.get_query_capability("adapter", select="dcterms:title")

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format="application/rdf+xml")

    assert g is not None

    ri = URIRef("http://localhost/oslc/services/provider/adapter/resources")

    assert (
        not (None, RDF.type, OSLC.ResponseInfo) in g
    ), "The ResponseInfo should not be generated"

    assert (ri, RDFS.member, None) in g, "The response does not contain a member"

    members = [m for m in g.objects(ri, RDFS.member)]
    assert members, "The ResponseInfo should have members"
    assert len(members) > 0, "The members should contain at least one element"

    for member in members:
        assert (
            len([o for o in g.objects(member, DCTERMS.title)]) == 1
        ), "Title should be in the resource description"


def test_query_capability_paging_select(pyoslc_enabled):
    response = pyoslc_enabled.get_query_capability(
        "adapter", paging=True, page_size=2, page_number=2, select="dcterms:title"
    )

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format="application/rdf+xml")

    assert g is not None

    ri = URIRef("http://localhost/oslc/services/provider/adapter/resources")

    assert (
        None,
        RDF.type,
        OSLC.ResponseInfo,
    ) in g, "The ResponseInfo should be generated"

    assert (ri, RDFS.member, None) in g, "The response does not contain a member"

    members = [m for m in g.objects(ri, RDFS.member)]
    assert members is not None, "The ResponseInfo should have members"
    assert len(members) > 0, "The members should contain at least one element"

    for member in members:
        assert (
            len([o for o in g.objects(member, DCTERMS.title)]) == 1
        ), "Title should be in the resource description"


def test_query_capability_destructured(pyoslc_enabled):
    response = pyoslc_enabled.get_query_capability(
        "adapter",
        prefixes=quote(
            "oslc_rm=<http://open-services.net/ns/rm#>,contact_plm=<https://contact-software.com/ontologies/v1.0/plm#>".encode(
                "UTF-8"
            )
        ),
        select="dcterms:title, dcterms:creator{foaf:firstName}, oslc_rm:discipline",
    )

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format="application/rdf+xml")

    assert g is not None

    ri = URIRef("http://localhost/oslc/services/provider/adapter/resources")
    assert (ri, RDFS.member, None) in g, "The response does not contain a member"

    predicate = URIRef("http://open-services.net/ns/rm#discipline")
    discipline = g.subject_objects(predicate=predicate)

    assert discipline is not None, "discipline attribute should be in the response"

    predicate = URIRef("http://purl.org/dc/terms/description")
    description = g.subject_objects(predicate=predicate)

    assert (
        len([t for t in description]) == 0
    ), "description attribute should no be in the response"


def test_creation_factory(pyoslc_enabled):
    """
    GIVEN the PyOSLC API
    WHEN requesting the creation factory endpoint to create a new
         resource on the graph within a specific project id
    THEN
        validating the status code of the response
        parsing the response content into a graph in the application/rdf+xml format
        validating whether the resource has the Requirement type
        validating that the resource has the identifier attribute
    """

    response = pyoslc_enabled.create("adapter")
    assert response is not None
    assert response.status_code == 201

    assert response.headers.get("location") is not None
    assert response.headers.get("etag") is not None

    g = Graph()
    g.parse(data=response.data, format="text/turtle")

    assert g is not None

    ri = URIRef("http://localhost/oslc/services/provider/adapter/resources/X1C2V3B6")

    assert (
        None,
        RDF.type,
        OSLC_RM.Requirement,
    ) in g, "The Requirement should be generated"
    assert (
        ri,
        DCTERMS.identifier,
        Literal("X1C2V3B6"),
    ) in g, "The response does not contain a identifier"
