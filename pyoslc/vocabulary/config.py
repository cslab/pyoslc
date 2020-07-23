from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

OSLC_CONFIG = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/config#"),
    terms=[
        # RDFS Classes in this namespace

        # RDF Properties in this namespace
        "cmServiceProviders",
    ]
)
