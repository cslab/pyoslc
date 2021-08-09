from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

OSLC_CONFIG = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/config#"),
    terms=[
        # RDFS Classes in this namespace
        "Configuration",
        "Stream",

        # RDF Properties in this namespace
        "cmServiceProviders",
    ]
)

PROV = ClosedNamespace(
    uri=URIRef("http://www.w3.org/ns/prov#"),
    terms=[
        "wasDerivedFrom", "wasRevisionOf", "wasGeneratedBy"
    ]
)
