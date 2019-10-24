from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

JAZZ_DISCOVERY = ClosedNamespace(
    uri=URIRef("http://jazz.net/xmlns/prod/jazz/discovery/1.0/"),
    terms=[
        # RDFS Classes in this namespace
        "Friend",

        # RDF Properties in this namespace
        # for Friends
        "friends", "rootServices",
    ]
)
