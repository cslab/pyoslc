from rdflib import Graph, URIRef, RDF

from pyoslc.vocabularies.config import OSLC_CONFIG
from pyoslc.vocabularies.core import OSLC
from pyoslc.vocabularies.jazz import JAZZ_CONFIG


def test_configuration_catalog(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN retrieving the service provider catalog for the configurations
    THEN
        validating the status code of the response
        parsing the response content into a graph in the application/rdf+xml format
        validating that the ServiceProviderCatalog is in the graph
        validating that the ServiceProvider for the components is in the graph
    """
    response = pyoslc.get_configuration_catalog()

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    assert g is not None

    cc = URIRef('http://localhost/oslc/services/config')
    comp = URIRef('http://localhost/oslc/services/config/components')

    assert (cc, RDF.type, OSLC.ServiceProviderCatalog) in g, 'The ServiceProviderCatalog is not in the graph'
    assert (cc, OSLC.serviceProvider, comp) in g, 'The ServiceProvider is not in the graph'


def test_configuration_components_container(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN retrieving the components container for the configurations
    THEN
        validating the status code of the response
        parsing the response content into a graph in the application/rdf+xml format
        validating that the ServiceProvider is in the graph
        validating that the Selection Dialog is in the graph
    """
    response = pyoslc.get_configuration_components()

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    assert g is not None

    comp = URIRef('http://localhost/oslc/services/config/components')
    dialog = URIRef('http://localhost/oslc/services/config/selection')

    assert (comp, RDF.type, OSLC.ServiceProvider) in g, 'The ServiceProvider is not in the graph'
    assert (None, OSLC.dialog, dialog) in g, 'The Selection Dialog is not in the graph'
    assert (None, OSLC.resourceType,
            JAZZ_CONFIG.Configuration) in g, 'The Configuration resource typeis not in the graph'


def test_configuration_components_selector(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN retrieving the selection endpoint
    THEN
        validating the status code of the response
        validating that the stream and baseline options are in the response
    """
    response = pyoslc.get_configuration_selection()

    assert response is not None
    assert response.status_code == 200
    assert b'Streams' in response.data
    assert b'Baseline' in response.data


def test_configuration_streams(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN retrieving the streams for the configurations
    THEN
        validating the status code of the response
        parsing the response content is a json with the list of streams
    """
    response = pyoslc.get_configuration_streams()

    assert response is not None
    assert response.status_code == 200

    result = response.json

    assert result is not None
    assert 'oslc:results' in result.keys()

    streams = [t for t in result['oslc:results']]
    types = [s['rdf:type'] for s in streams if s['rdf:type'] != None]

    assert "http://open-services.net/ns/config#Stream" in types


def test_configuration_stream_detail(pyoslc):
    """
    GIVEN the PyOSLC API
    WHEN retrieving a specific stream endpoint
    THEN
        validating the status code of the response
        parsing the response content into a graph in the application/rdf+xml format
        validating that the Configuration type is in the graph
        validating that the Stream type is in the graph
    """
    response = pyoslc.get_stream(1)

    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    assert g is not None

    stream = URIRef('http://localhost/oslc/services/config/stream/1')

    assert (stream, RDF.type, OSLC_CONFIG.Configuration) in g, 'The Configuration type is not in the graph'
    assert (stream, RDF.type, OSLC_CONFIG.Stream) in g, 'The Stream type is not in the graph'
