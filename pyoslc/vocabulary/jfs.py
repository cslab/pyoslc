from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

JFS = ClosedNamespace(
    uri=URIRef("http://jazz.net/xmlns/prod/jazz/jfs/1.0/"),
    terms=[
        # RDFS Classes in this namespace

        # RDF Properties in this namespace
        # for OAuth
        "oauthRealmName", "oauthDomain",
        "oauthRequestConsumerKeyUrl",
        "oauthApprovalModuleUrl",
        "oauthRequestTokenUrl",
        "oauthUserAuthorizationUrl",
        "oauthAccessTokenUrl"
    ]
)
