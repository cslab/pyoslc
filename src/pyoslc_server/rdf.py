from rdflib import Graph, RDF, DCTERMS, URIRef, Literal
from rdflib.resource import Resource

from pyoslc.vocabularies.rm import OSLC_RM


def to_rdf(subject, attr_mapping, rdf_type, oslc_domain, rdf_format, *args, **kwargs):

    if len(args) == 1:
        data = args[0]

    graph = Graph()
    graph.bind('rdf', RDF)
    graph.bind('dcterms', DCTERMS)
    graph.bind('oslc_rm', OSLC_RM)

    r = Resource(graph, URIRef(subject))
    if isinstance(rdf_type, list):
        for type in rdf_type:
            r.add(RDF.type, type)
    else:
        r.add(RDF.type, OSLC_RM.Requirement)

    r.add(RDF.about, URIRef(subject))

    for field, property in attr_mapping.items():
        r.add(property, Literal(getattr(data, field)))

    return graph.serialize(format=rdf_format)
