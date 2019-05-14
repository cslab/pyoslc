"""
    Vocabulary definition for the OSLC specification.

    Taken from:
    http://docs.oasis-open.org/oslc-core/oslc-core/v3.0/csprd03/part7-core-vocabulary/oslc-core-v3.0-csprd03-part7-core-vocabulary.html#rdfvocab
    http://docs.oasis-open.org/oslc-core/oslc-core/v3.0/csprd03/part7-core-vocabulary/oslc-core-v3.0-csprd03-part7-core-vocabulary.html#vocabulary-details

"""
from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

OSLCCore = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/core#"),
    terms=[
        # RDFS Classes in this namespace
        "AllowedValues", "AttachmentContainer", "AttachmentDescriptor",
        "Comment", "Compact", "CreationFactory", "Dialog",
        "Discussion", "Error", "ExtendedError", "OAuthConfiguration",
        "PrefixDefinition", "Preview", "Property", "Publisher",
        "QueryCapability", "ResourceShape", "ResponseInfo",
        "Service", "ServiceProvider", "ServiceProviderCatalog",

        # RDF Properties in this namespace
        "allowedValue", "allowedValues", "archived", "attachment", "attachmentSize",
        "authorizationURI", "comment", "creation", "creationDialog", "creationFactory",
        "default", "defaultValue", "describes", "details", "dialog", "discussedBy",
        "discussionAbout", "document", "domain", "error", "executes", "extendedError",
        "futureAction", "hidden", "hintHeight", "hintWidth", "icon", "iconAltLabel",
        "iconSrcSet", "iconTitle", "impactType", "initialHeight", "inReplyTo",
        "instanceShape", "inverseLabel", "isMemberProperty", "label", "largePreview",
        "maxSize", "message", "modifiedBy", "moreInfo", "name", "nextPage",
        "oauthAccessTokenURI", "oauthConfiguration", "oauthRequestTokenURI", "occurs",
        "partOfDiscussion", "postBody", "prefix", "prefixBase", "prefixDefinition",
        "property", "propertyDefinition", "queryable", "queryBase", "queryCapability",
        "range", "readOnly", "rel", "representation", "resourceShape", "resourceType",
        "results", "selectionDialog", "service", "serviceProvider", "serviceProviderCatalog",
        "shortId", "shortTitle", "smallPreview", "statusCode", "totalCount", "usage",
        "valueShape", "valueType"
    ]
)

OSLCData = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/servicemanagement/1.0/"),
    terms=[
        # RDFS Classes in this namespace
        # RDF Properties in this namespace
    ]
)

OSLC_AM = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/am#"),
    terms=[
        # RDFS Classes in this namespace
        # RDF Properties in this namespace
    ]
)

OSLC_CM = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/cm#"),
    terms=[
        # RDFS Classes in this namespace
        # RDF Properties in this namespace
    ]
)

OSLC_RM = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/rm#"),
    terms=[
        # RDFS Classes in this namespace
        # RDF Properties in this namespace
    ]
)