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
    assert (ri, DCTERMS.title, None) in g, 'The ResponseInfo should have a title'

    members = [m for m in g.objects(ri, RDFS.member)]
    assert members is not None, 'The ResponseInfo should have members'

    m1 = URIRef(ri + '/X1C2V3B1')
    m2 = URIRef(ri + '/X1C2V3B2')
    m3 = URIRef(ri + '/X1C2V3B3')

    assert m1 in members, 'The ResponseInfo does not contain the member X1C2V3B1'
    assert m2 in members, 'The ResponseInfo does not contain the member X1C2V3B1'
    assert m3 in members, 'The ResponseInfo does not contain the member X1C2V3B1'


def test_creation_factory(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN requesting the creation factory endpoint to create a new
         resource on the graph within a specific project id
    THEN
        validating the status code of the response
        parsing the response content into a graph in the application/rdf+xml format
        validating whether the ResponseInfo statement is within the graph
        validating that the member attribute is present on the graph
        validating that at least the first three records from the csv file are present
    """

    payload = """
    <rdf:RDF 
        xmlns:oslc_rm="http://open-services.net/ns/rm#"
        xmlns:dcterms="http://purl.org/dc/terms/"
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        
        <oslc_rm:Requirement rdf:about="http://localhost/oslc/services/provider/Project-1/resources/requirement/X1C2V3B3">
            <oslc_rm:satisfiedBy>Software Development</oslc_rm:satisfiedBy>
            <dcterms:description>The OSLC RM Specification needs to be awesome 3</dcterms:description>
            <oslc_rm:constrainedBy>Customer Requirement</oslc_rm:constrainedBy>
            <oslc_rm:trackedBy>0</oslc_rm:trackedBy>
            <oslc_rm:validatedBy>1</oslc_rm:validatedBy>
            <dcterms:title>The SAFER FTA should not limit EVA crewmember mobility</dcterms:title>
            <oslc_rm:affectedBy>0</oslc_rm:affectedBy>
            <dcterms:shortTitle>SDK-Dev</dcterms:shortTitle>
            <dcterms:creator>Mario</dcterms:creator>
            <dcterms:subject>Project-1</dcterms:subject>
            <oslc_rm:elaboratedBy>Ian Altman</oslc_rm:elaboratedBy>
            <dcterms:identifier>X1C2V3B3</dcterms:identifier>
            <oslc_rm:decomposedBy>Draft</oslc_rm:decomposedBy>
        </oslc_rm:Requirement>
    </rdf:RDF>
    """

    response = pyoslc.post_creation_factory('Project-1', payload)
    assert response is not None
    assert response.status_code == 201

    assert response.headers.get('etag') is not None
