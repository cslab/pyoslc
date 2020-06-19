from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

OSLC_TRS = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/core/trs#"),
    terms=[
        # RDFS Classes in this namespace
        "ResourceSet", "Resource",
        "TrackedResourceSet", "ChangeLog",
        "Creation", "Modification", "Deletion",

        # RDF Properties in this namespace
        "trackedResourceSet",

        "base", "changeLog", "cutoffEvent",
        "change", "previous", "changed", "order",

    ]
)
