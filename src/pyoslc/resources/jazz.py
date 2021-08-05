from flask import url_for
from rdflib import URIRef, Literal, BNode, RDF
from rdflib.namespace import DCTERMS
from rdflib.resource import Resource

from app.api.adapter.vocabulary import PYOSLC
from pyoslc.resources.models import BaseResource
from pyoslc.vocabularies.am import OSLC_AM
from pyoslc.vocabularies.cm import OSLC_CM
from pyoslc.vocabularies.config import OSLC_CONFIG
from pyoslc.vocabularies.core import OSLC
from pyoslc.vocabularies.jazz import JAZZ_DISCOVERY, OSLC_RM_JAZZ, OSLC_CM_JAZZ
from pyoslc.vocabularies.jfs import JFS
from pyoslc.vocabularies.rm import OSLC_RM
from pyoslc.vocabularies.trs import OSLC_TRS


class RootService(BaseResource):

    def __init__(self, about=None, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None, friends=None,
                 publisher=None, service=None, details=None, prefix_definition=None, oauth_configuration=None):
        """
        Initialize Root Service
        """

        super(RootService, self).__init__(about, types, properties, description, identifier, short_title, title,
                                          contributor, creator, subject, created, modified, type, discussed_by,
                                          instance_shape, service_provider, relation)

        self.__friends = friends or list()
        self.__publisher = publisher or ''

    @property
    def friends(self):
        return self.__friends

    @friends.setter
    def friends(self, friends):
        self.__friends = friends

    def add_friend(self, friend):
        self.__friends.append(friend)

    @property
    def publisher(self):
        return self.__publisher

    @publisher.setter
    def publisher(self, publisher):
        self.__publisher = publisher

    def to_rdf(self, graph):

        graph.bind('dc', DCTERMS)
        graph.bind('jd', JAZZ_DISCOVERY)

        uri = self.about if self.about.__contains__(self.identifier) else self.about + '/{}'.format(
            self.identifier) if self.identifier else ''

        rs = Resource(graph, URIRef(uri))

        if self.title:
            rs.add(DCTERMS.title, Literal(self.title))

        if self.description:
            rs.add(DCTERMS.description, Literal(self.description))

        if self.publisher:
            publisher_url = url_for('oslc.adapter_configuration_publisher', _external=True)
            rs.add(OSLC.publisher, URIRef(publisher_url))

        graph.bind('oslc_am', OSLC_AM)
        graph.bind('oslc_rm', OSLC_RM_JAZZ, override=True)
        graph.bind('oslc_cm', OSLC_CM_JAZZ, override=True)
        graph.bind('oslc_config', OSLC_CONFIG)
        graph.bind('jfs', JFS)
        graph.bind('trs', OSLC_TRS)
        graph.bind('pyoslc', PYOSLC)

        spc_url = url_for('oslc.adapter_service_provider_catalog', _external=True)
        spc_config_url = url_for('oslc.adapter_configuration_catalog', _external=True)

        rs.add(OSLC_RM_JAZZ.rmServiceProviders, URIRef(spc_url))
        rs.add(OSLC_CONFIG.cmServiceProviders, URIRef(spc_config_url))

        rs.add(JFS.oauthRealmName, Literal("PyOSLC"))
        rs.add(JFS.oauthDomain, Literal(url_for('oslc.doc', _external=True)))
        rs.add(JFS.oauthRequestConsumerKeyUrl, URIRef(url_for('consumer.register', _external=True)))
        rs.add(JFS.oauthApprovalModuleUrl, URIRef(url_for('consumer.approve', _external=True)))
        rs.add(JFS.oauthRequestTokenUrl, URIRef(url_for('oauth.issue_token', _external=True)))
        rs.add(JFS.oauthUserAuthorizationUrl, URIRef(url_for('oauth.issue_token', _external=True)))
        rs.add(JFS.oauthAccessTokenUrl, URIRef(url_for('oauth.issue_token', _external=True)))

        trs = Resource(graph, BNode())
        trs.add(RDF.type, PYOSLC.TrackedResourceSetProvider)

        trs_url = URIRef(url_for('oslc.doc', _external=True))

        tr = Resource(graph, BNode())
        tr.add(RDF.type, OSLC_TRS.TrackedResourceSet)
        tr.add(OSLC_TRS.trackedResourceSet, URIRef(trs_url))

        # # trs.add(RDF.type, OSLC_TRS.TrackedResourceSet)
        # # trs.add(DCTERMS.title, Literal('Title', datatype=XSD.Literal))
        tr.add(DCTERMS.title, Literal('Title'))
        tr.add(DCTERMS.description, Literal('Description'))

        tr.add(DCTERMS.type, URIRef(OSLC_CM.uri) if isinstance(OSLC_CM.uri, str) else OSLC_CM.uri)
        tr.add(OSLC.domain, URIRef(OSLC_RM.uri) if isinstance(OSLC_RM.uri, str) else OSLC_RM.uri)
        tr.add(OSLC.domain, URIRef(OSLC_AM.uri) if isinstance(OSLC_AM.uri, str) else OSLC_AM.uri)

        trs.add(OSLC_TRS.TrackedResourceSet, tr)
        rs.add(PYOSLC.TrackedResourceSetProvider, trs)

        return rs
