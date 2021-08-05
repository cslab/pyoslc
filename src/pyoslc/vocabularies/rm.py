from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

OSLC_RM = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/rm#"),
    terms=[
        # RDFS Classes in this namespace
        "Requirement", "RequirementCollection",

        # RDF Properties in this namespace
        # for Requirement
        "affectedBy", "elaboratedBy", "implementedBy",
        "specifiedBy", "satisfiedBy", "trackedBy",
        "validatedBy",

        # for RequirementCollection
        "uses",
        # General
        "elaborates", "specifies", "satisfies",
        "decomposedBy", "decomposes",
        "constrainedBy", "constrains",
        "rmServiceProviders",
    ]
)
