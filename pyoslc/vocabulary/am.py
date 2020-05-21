from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

OSLC_AM = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/am#"),
    terms=[
        # RDFS Classes in this namespace
        "LinkType",

        # RDF Properties in this namespace
        "amServiceProviders",
    ]
)
