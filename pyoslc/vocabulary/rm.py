from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

OSLC_RM = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/rm#"),
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