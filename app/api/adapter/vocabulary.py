from rdflib import URIRef
from rdflib.namespace import ClosedNamespace


PYOSLC = ClosedNamespace(
    uri=URIRef("http://example.com/ns/pyoslc#"),
    terms=[
        "TrackedResourceSetProvider",
    ],
)
