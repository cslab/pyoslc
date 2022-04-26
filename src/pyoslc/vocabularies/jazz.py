from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

JAZZ_DISCOVERY = ClosedNamespace(
    uri=URIRef("http://jazz.net/xmlns/prod/jazz/discovery/1.0/"),
    terms=[
        # RDFS Classes in this namespace
        "Friend",
        "RootServices",
        # RDF Properties in this namespace
        # for Friends
        "friends",
        "rootServices",
    ],
)

JAZZ_PROCESS = ClosedNamespace(
    uri=URIRef("http://jazz.net/xmlns/prod/jazz/process/1.0/"),
    terms=[
        "supportContributionsToLinkIndexProvider",
        "supportLinkDiscoveryViaLinkIndexProvider",
        "globalConfigurationAware",
        "supportOSLCSimpleQuery",
    ],
)

OSLC_RM_JAZZ = ClosedNamespace(
    uri=URIRef("http://open-services.net/xmlns/rm/1.0/"), terms=["rmServiceProviders"]
)

OSLC_CM_JAZZ = ClosedNamespace(
    uri=URIRef("http://open-services.net/xmlns/cm/1.0/"), terms=[]
)

JAZZ_CONFIG = ClosedNamespace(
    uri=URIRef("http://jazz.net/ns/vvc#"), terms=["Configuration"]
)
