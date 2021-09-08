import pytest
from rdflib import Graph, RDF, URIRef, DCTERMS, RDFS, Literal

from pyoslc.vocabularies.core import OSLC
from pyoslc.vocabularies.jazz import JAZZ_PROCESS
from pyoslc.vocabularies.rm import OSLC_RM


@pytest.mark.skip(reason="GET Resource was moved to the new PyOSLC OSLCAPP framework")
def test_serializer_plugin_exception(pyoslc):
    """
    GIVEN the PyOSLC API and an invalid RDF representation
    WHEN requesting the catalog endpoint for getting the ServiceProviderCatalog
    THEN
        validating the status code of the response which should be BAD REQUEST (400)
    """

    representation = 'jsonld'

    response = pyoslc.get_catalog(representation)

    assert response is not None
    assert response.status_code == 415
    assert b'message' in response.data
    assert b'The server does not support the media type' in response.data


@pytest.mark.skip(reason="GET Resource was moved to the new PyOSLC OSLCAPP framework")
def test_unsupported_media_type(pyoslc):
    """
    GIVEN the PyOSLC API and an invalid RDF representation
    WHEN requesting the catalog endpoint for getting the ServiceProviderCatalog
    THEN
        validating the status code of the response which should be 415
    """

    response = pyoslc.get_catalog('application/rdf')
    assert response is not None
    assert response.status_code == 415


@pytest.mark.skip(reason="GET Resource was moved to the new PyOSLC OSLCAPP framework")
def test_service_provider_catalog(pyoslc):
    """
    GIVEN the PyOSLC API and a list of RDF representations
    WHEN requesting the catalog endpoint for getting the ServiceProviderCatalog
    THEN
        validating the status code of the response
        parsing the response content into a graph in the rdf representation format
        validating whether the ServiceProviderCatalog statement is within the graph
    """

    representations = ['application/rdf+xml', 'application/json-ld', 'text/turtle']

    for representation in representations:

        response = pyoslc.get_catalog(representation)
        assert response is not None
        assert response.status_code == 200

        g = Graph()
        g.parse(data=response.data, format=representation if representation != 'application/json-ld' else 'json-ld')

        assert g is not None

        spc = URIRef('http://localhost/oslc/services/catalog')

        assert (spc, RDF.type, OSLC.ServiceProviderCatalog) in g, 'The ServiceProviderCatalog was not generated'
        assert (spc, OSLC.serviceProvider, None) in g, 'The response does not contain a ServiceProvider'
        assert (spc, OSLC.domain, URIRef(OSLC_RM.uri) if isinstance(OSLC_RM.uri, str) else OSLC_RM.uri) in g, 'The ServiceProvider is not on RM domain'

        assert 'Service Provider Catalog' in [t for t in g.objects(spc, DCTERMS.title)][0]
        assert 'Project-1' in [t for t in g.objects(spc, OSLC.serviceProvider)][0]


@pytest.mark.skip(reason="GET Resource was moved to the new PyOSLC OSLCAPP framework")
def test_bad_service_provider(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN requesting the service provider endpoint for getting the ServiceProvider
         with a non existent id
    THEN
        validating the status code of the response that should be 404
    """

    response = pyoslc.get_service_provider('Project-1a')
    assert response is not None
    assert response.status_code == 404
    assert b'No resources with ID' in response.data


@pytest.mark.skip(reason="GET Resource was moved to the new PyOSLC OSLCAPP framework")
def test_service_provider(pyoslc):
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

    response = pyoslc.get_service_provider('Project-1')
    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    assert g is not None

    sp = URIRef('http://localhost/oslc/services/provider/Project-1')

    assert (None, RDF.type, OSLC.ServiceProviderCatalog) not in g, 'The ServiceProviderCatalog should not be generated'
    assert (sp, RDF.type, OSLC.ServiceProvider) in g, 'The ServiceProvider was not generated'
    assert (sp, OSLC.service, None) in g, 'The response does not contain a Service'
    assert (sp, DCTERMS.identifier, None) in g, 'The ServiceProvider should have a identifier'

    assert (sp, JAZZ_PROCESS.globalConfigurationAware, None) in g, 'The globalConfigurationAware should be present'
    assert (sp, JAZZ_PROCESS.supportContributionsToLinkIndexProvider, None) in g, \
        'The supportContributionsToLinkIndexProvider attribute should be present'
    assert (sp, JAZZ_PROCESS.supportLinkDiscoveryViaLinkIndexProvider, None) in g, \
        'The supportLinkDiscoveryViaLinkIndexProvider attribute should be present'

    assert 'Project-1' in [t for t in g.objects(sp, DCTERMS.identifier)][0]


@pytest.mark.skip(reason="GET Resource was moved to the new PyOSLC OSLCAPP framework")
def test_query_capability(pyoslc):
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

    response = pyoslc.get_query_capability('Project-1')
    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    assert g is not None

    ri = URIRef('http://localhost/oslc/services/provider/Project-1/resources/requirement')

    assert (None, RDF.type, OSLC.ResponseInfo) in g, 'The ResponseInfo should be generated'

    assert (ri, RDFS.member, None) in g, 'The response does not contain a member'
    assert (ri, OSLC.totalCount, None) in g, 'The response does not contain the totalCount'
    assert (ri, DCTERMS.title, None) in g, 'The ResponseInfo should have a title'

    members = [m for m in g.objects(ri, RDFS.member)]
    assert members is not None, 'The ResponseInfo should have members'

    m1 = URIRef(ri + '/X1C2V3B1')
    m2 = URIRef(ri + '/X1C2V3B2')
    m3 = URIRef(ri + '/X1C2V3B3')

    assert m1 in members, 'The ResponseInfo does not contain the member X1C2V3B1'
    assert m2 in members, 'The ResponseInfo does not contain the member X1C2V3B1'
    assert m3 in members, 'The ResponseInfo does not contain the member X1C2V3B1'


@pytest.mark.skip(reason="POST Resource was moved to the new PyOSLC OSLCAPP framework")
def test_creation_factory(pyoslc):
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

    response = pyoslc.create('Project-1')
    assert response is not None
    assert response.status_code == 201

    assert response.headers.get('location') is not None
    assert response.headers.get('etag') is not None

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    assert g is not None

    ri = URIRef('http://localhost/oslc/services/provider/Project-1/resources/requirement/X1C2V3B6')

    assert (None, RDF.type, OSLC_RM.Requirement) in g, 'The Requirement should be generated'
    assert (ri, DCTERMS.identifier, Literal('X1C2V3B6')) in g, 'The response does not contain a identifier'

    response = pyoslc.delete('Project-1', 'X1C2V3B6')
    assert response is not None
    assert response.status_code == 200


@pytest.mark.skip(reason="GET Resource method has not been implemented with the new PyOSLC OSLCAPP framework")
def test_query_resource(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN requesting the query capability endpoint for getting a
         specific Resource given the project and resource id
    THEN
        validating the status code of the response
        parsing the response content into a graph in the application/rdf+xml format
        validating whether the Requirement type is within the graph
        validating that the identifier is in the response
    """

    response = pyoslc.get_query_resource('Project-1', 'X1C2V3B1')
    assert response is not None
    assert response.status_code == 200

    assert response.headers.get('etag') is not None

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    assert g is not None

    ri = URIRef('http://localhost/oslc/services/provider/Project-1/resources/requirement/X1C2V3B1')

    assert (None, RDF.type, OSLC_RM.Requirement) in g, 'The Requirement should be generated'
    assert (ri, DCTERMS.identifier, Literal('X1C2V3B1')) in g, 'The response does not contain a identifier'


@pytest.mark.skip(reason="UPDATE method has not been implemented with the new PyOSLC OSLCAPP framework")
def test_update_resource(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN requesting the resource endpoint with put method to update a
         resource on the graph within a specific project id
    THEN
        validating the status code of the response
        parsing the response content into a graph in the application/rdf+xml format
        validating whether the response contains the Requirement type
        validating that the resource has the identifier
        validating that the content of the short_title has the updated value
    """

    response = pyoslc.create('Project-1')
    assert response is not None
    assert response.status_code == 201

    assert response.headers.get('location') is not None
    assert response.headers.get('etag') is not None

    etag = response.headers.get('etag')

    response = pyoslc.update('Project-1', etag)
    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    assert g is not None

    ri = URIRef('http://localhost/oslc/services/provider/Project-1/resources/requirement/X1C2V3B6')

    assert (None, RDF.type, OSLC_RM.Requirement) in g, 'The Requirement should be generated'
    assert (ri, DCTERMS.identifier, Literal('X1C2V3B6')) in g, 'The response does not contain a identifier'

    short_title = [st for st in g.objects(ri, OSLC.shortTitle)]
    assert short_title is not None, 'The resource should have a title'

    assert '[[UPDATED]] - SDK-Dev' == short_title[0].value, 'The response does not contain a identifier'

    response = pyoslc.delete('Project-1', 'X1C2V3B6')
    assert response is not None
    assert response.status_code == 200


@pytest.mark.skip(reason="DELETE method has not been implemented with the new PyOSLC OSLCAPP framework")
def test_delete_resource(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN requesting the resource endpoint with delete method to
         delete the resource from the graph within a specific project id
    THEN
        validating the status code of the response
        validating the message of the deleted resource
    """

    response = pyoslc.create('Project-1')
    assert response is not None
    assert response.status_code == 201

    response = pyoslc.delete('Project-1', 'X1C2V3B6')
    assert response is not None
    assert response.status_code == 200
    assert b'Resource deleted' in response.data
