from rdflib import Graph, URIRef, RDF, DCTERMS

from app.api.adapter.vocabulary import PYOSLC
from pyoslc.vocabularies.am import OSLC_AM
from pyoslc.vocabularies.cm import OSLC_CM
from pyoslc.vocabularies.config import OSLC_CONFIG
from pyoslc.vocabularies.core import OSLC
from pyoslc.vocabularies.jazz import OSLC_RM_JAZZ
from pyoslc.vocabularies.jfs import JFS
from pyoslc.vocabularies.rm import OSLC_RM
from pyoslc.vocabularies.trs import OSLC_TRS


def test_unsupported_media_type(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN retrieving any endpoint with an invalid content-type
    THEN
        validating the status code of the response which should be 415
    """
    response = pyoslc.get_rootservices('application/rdf')
    assert response is not None
    assert response.status_code == 415


def test_rootservices(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN requesting the rootservices endpoint
    THEN
        validating the status code of the response
        parsing the response content into a graph in the application/rdf+xml format
        validating whether the Publisher statement is  within the graph
        validating that the RM ServiceProvider is within the graph
        validating the attributes for the integration with a global configuration project
    """

    response = pyoslc.get_rootservices()

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    assert g is not None

    rs = URIRef('http://localhost/oslc/services/rootservices')

    assert (None, RDF.type, OSLC.ServiceProviderCatalog) not in g, 'The ServiceProviderCatalog should not be generated'
    #assert (re, RDF.type, OSLC.ServiceProvider) in g, 'The ServiceProvider was not generated'
    assert (rs, OSLC.publisher, None) in g, 'The Publisher was not added'
    assert (rs, OSLC_RM_JAZZ.rmServiceProviders, None) in g, 'The RM ServiceProvider was not added'
    assert (rs, OSLC_CONFIG.cmServiceProviders, None) in g, 'The CM ServiceProvider was not added'

    assert (rs, JFS.oauthRealmName, None) in g, 'The OAuth RealName was not added'
    rn = [o for o in g.objects(rs, JFS.oauthRealmName)][0]

    assert rn.value == 'PyOSLC'

    assert (rs, JFS.oauthDomain, None) in g, 'The OAuth Domain was not added'
    assert (rs, JFS.oauthRequestConsumerKeyUrl, None) in g, 'The OAuth Request Consumer Key endpoint was not added'
    assert (rs, JFS.oauthApprovalModuleUrl, None) in g, 'The OAuth Approval endpoint was not added'
    assert (rs, JFS.oauthRequestTokenUrl, None) in g, 'The OAuth Request Token endpoint was not added'
    assert (rs, JFS.oauthUserAuthorizationUrl, None) in g, 'The OAuth Request Token endpoint was not added'

    assert (None, RDF.type, PYOSLC.TrackedResourceSetProvider) in g, 'The TRS Provider endpoint was not added'
    assert (None, RDF.type, OSLC_TRS.TrackedResourceSet) in g, 'The TRS endpoint was not added'

    assert (None, DCTERMS.type, OSLC_CM.uri) in g, 'The CM type was not added'
    assert (None, OSLC.domain, OSLC_RM.uri) in g, 'The RM Domain was not added'
    assert (None, OSLC.domain, OSLC_AM.uri) in g, 'The AM Domain was not added'


def test_publisher(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN retrieving the publisher endpoint
    THEN
        validating that the response status is ok
        validating that the response in on rdf+xml representation
        the type in the graph is Publisher
    """
    response = pyoslc.get_publisher()

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    assert g is not None

    p = URIRef('http://localhost/oslc/services/config/publisher')

    assert (p, RDF.type, OSLC.Publisher) in g, 'The Publisher type is not in the graph'
    assert (p, JFS.version, None) in g, 'The version of JFS is not in the graph'


def test_consumer_register(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN requesting the creation of a consumer
    THEN
        validating the status code of the response
        parsing the response content into json
        validating the key content in the response
    """

    response = pyoslc.create_consumer()

    assert response is not None
    assert response.status_code == 200

    assert 'key' in response.json.keys(), 'The response should contain the key element'


def test_associations(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN receiving the request to create an association with a jazz application
    THEN
        validating the rootservices content
        taking the rm/qm service provider to retrieve the container
        showing the container for selection
    """

    response = pyoslc.get_rootservices()

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    rs = URIRef('http://localhost/oslc/services/rootservices')
    rm_catalog = URIRef('http://localhost/oslc/services/catalog')
    cfg_catalog = URIRef('http://localhost/oslc/services/config')

    rm = [s for s in g.objects(rs, OSLC_RM_JAZZ.rmServiceProviders)][0]
    cfg = [s for s in g.objects(rs, OSLC_CONFIG.cmServiceProviders)][0]

    assert rm is not None
    assert rm == rm_catalog
    assert cfg == cfg_catalog

    response = pyoslc.get_catalog()

    assert response is not None
    assert response.status_code == 200

    response = pyoslc.get_configuration_catalog()

    assert response is not None
    assert response.status_code == 200


def test_link_target_selector(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN accessing to the link section on a jazz application
    THEN
        generating the rootservices response
        taking the catalog endpoint for rm/qm to retrieve the service provider
        validating the service provider for seeing the query capability of the resource
        retrieving the selector and creator endpoints for a resource
    """
    response = pyoslc.get_rootservices()

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    rs = URIRef('http://localhost/oslc/services/rootservices')
    rm_catalog = URIRef('http://localhost/oslc/services/catalog')
    sp_container = URIRef('http://localhost/oslc/services/provider/Project-1')

    rm = [s for s in g.objects(rs, OSLC_RM_JAZZ.rmServiceProviders)][0]

    assert rm is not None
    assert rm == rm_catalog

    response = pyoslc.get_catalog()

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    sp = [s for s in g.objects(rm_catalog, OSLC.serviceProvider)][0]

    assert sp is not None
    assert sp == sp_container

    response = pyoslc.get_service_provider('Project-1')

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    sd = [s for s in g.subject_objects(OSLC.selectionDialog)][0]
    cd = [s for s in g.subject_objects(OSLC.creationDialog)][0]

    assert sd is not None
    assert cd is not None

    selector = [s for s in g.objects(sd[1], OSLC.dialog)][0]

    response = pyoslc.get(selector)

    assert response is not None
    assert response.status_code == 200
    assert b'Find a specific resource through a free-text search.' in response.data


def test_show_preview(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN retrieving the small and large preview endpoints
    THEN
        validating the status code of the response
        validating that teh content of the small preview only contain two data
        validating that teh content of the large preview only contain four data
    """
    project_id = 'Project-1'
    resource_id = 'X1C2V3B1'
    preview_type = 'smallPreview'

    url = 'http://localhost/oslc/services/provider/{}/resources/requirement/{}/{}'.format(project_id, resource_id,
                                                                                          preview_type)

    response = pyoslc.get(url)
    assert response is not None
    assert response.status_code == 200
    assert resource_id.encode('ascii') in response.data
    assert b'Specification ID' in response.data
    assert b'Description' in response.data
    assert b'Title' not in response.data
    assert b'Product' not in response.data

    preview_type = 'largePreview'

    url = 'http://localhost/oslc/services/provider/{}/resources/requirement/{}/{}'.format(project_id, resource_id,
                                                                                          preview_type)

    response = pyoslc.get(url)
    assert response is not None
    assert response.status_code == 200
    assert b'Specification ID' in response.data
    assert resource_id.encode('ascii') in response.data
    assert b'Description' in response.data
    assert b'Title' in response.data
    assert b'Product' in response.data




