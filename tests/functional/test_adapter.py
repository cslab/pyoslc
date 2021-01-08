from rdflib import Graph, RDF, URIRef, DCTERMS, RDFS

from pyoslc.vocabularies.core import OSLC
from pyoslc.vocabularies.jazz import JAZZ_PROCESS
from pyoslc.vocabularies.rm import OSLC_RM


def test_service_provider_catalog(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN requesting the catalog endpoint for getting the ServiceProviderCatalog
    THEN
        validating the status code of the response
        parsing the response content into a graph in the application/rdf+xml format
        validating whether the ServiceProviderCatalog statement is within the graph
    """

    response = pyoslc.get_catalog()
    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    assert g is not None

    spc = URIRef('http://localhost/oslc/services/catalog')

    assert (spc, RDF.type, OSLC.ServiceProviderCatalog) in g, 'The ServiceProviderCatalog was not generated'
    assert (spc, OSLC.serviceProvider, None) in g, 'The response does not contain a ServiceProvider'
    assert (spc, OSLC.domain, OSLC_RM.uri) in g, 'The ServiceProvider is not on RM domain'

    assert 'Service Provider Catalog' in [t for t in g.objects(spc, DCTERMS.title)][0]
    assert 'Project-1' in [t for t in g.objects(spc, OSLC.serviceProvider)][0]


def test_service_provider(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN requesting the service provider endpoint for getting the ServiceProvider
         with a specific id
    THEN
        validating the status code of the response
        parsing the response content into a graph in the application/rdf+xml format
        validating whether the ServiceProviderCatalog statement is within the graph
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


def test_query_capability(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN requesting the query capability endpoint for getting the
         list of Requirements with a specific project id
    THEN
        validating the status code of the response
        parsing the response content into a graph in the application/rdf+xml format
        validating whether the ServiceProviderCatalog statement is within the graph
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
    assert (ri, DCTERMS.title, None) in g, 'The ResponseInfo should have a title'

    assert [t for t in g.objects(ri, RDFS.member)] is not None, 'The ResponseInfo should have members'
