from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

OSLC_RM = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/rm#"),
    terms=[
        # RDFS Classes in this namespace
        "Requirement", "RequirementCollection",

        # RDF Properties in this namespace
        # for Requirement
        "elaboratedBy", "elaborates",
        "specifiedBy", "specifies",
        "affectedBy", "trackedBy", "implementedBy", "validatedBy",
        "satisfiedBy", "satisfies",
        "decomposedBy", "decomposes",
        "constrainedBy", "constrains",

        # for RequirementCollection
        "uses"
    ]
)
