from rdflib import Graph, RDF

from pyoslc.vocabularies.core import OSLC


def test_service_provider_catalog(pyoslc):
    response = pyoslc.get_catalog()
    assert response is not None
    assert response.status_code == 200

    g = Graph()
    g.parse(data=response.data, format='application/rdf+xml')

    assert g is not None

    spc = [s for s in g.subjects(RDF.type, OSLC.ServiceProviderCatalog)]
    sp = [s for s in g.subjects(RDF.type, OSLC.ServiceProvider)]

    assert spc is not None
    assert sp is not None


def test_service_provider(pyoslc):
    response = pyoslc.get_service_provider('Project-1')

    assert response is not None
    assert response.status_code == 200
