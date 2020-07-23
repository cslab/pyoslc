from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

OAUTH = ClosedNamespace(
    uri=URIRef("http://koneksys.com/pyoslc/server/oauth#"),
    terms=[
        # RDFS Classes in this namespace
        "Consumer",

        # RDF Properties in this namespace
        "consumerName", "consumerKey",
        "consumerSecret", "provisional",
        "trusted", "callback"
    ]
)
