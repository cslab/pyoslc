from flask import url_for
from rdflib import URIRef, RDF, Literal, BNode
from rdflib.namespace import DCTERMS, XSD, Namespace
from rdflib.resource import Resource

from pyoslc.vocabulary import OSLCCore
from pyoslc.vocabulary.am import OSLC_AM
from pyoslc.vocabulary.cm import OSLC_CM
from pyoslc.vocabulary.config import OSLC_CONFIG
from pyoslc.vocabulary.jazz import JAZZ_DISCOVERY
from pyoslc.vocabulary.jfs import JFS
from pyoslc.vocabulary.rm import OSLC_RM
from pyoslc.vocabulary.trs import OSLC_TRS
from resource import Resource_


class RootService(Resource_):

    def __init__(self, about=None, types=None, properties=None,
                 description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None,
                 friends=None, service=None, details=None, prefix_definition=None, oauth_configuration=None):
        """
        Initialize Root Service
        """

        Resource_.__init__(self, about=about, types=types, properties=properties, description=description,
                           identifier=identifier, short_title=short_title, title=title, contributor=contributor,
                           creator=creator, subject=subject, created=created, modified=modified, type=type,
                           discussed_by=discussed_by, instance_shape=instance_shape, service_provider=service_provider,
                           relation=relation)

        self.__friends = friends or list()

    @property
    def friends(self):
        return self.__friends

    @friends.setter
    def friends(self, friends):
        self.__friends = friends

    def add_friend(self, friend):
        self.__friends.append(friend)

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

        OSLC_RM_JAZZ = Namespace("http://open-services.net/xmlns/rm/1.0/")
        OSLC_CM_JAZZ = Namespace("http://open-services.net/xmlns/cm/1.0/")

        graph.bind('oslc_am', OSLC_AM)
        graph.bind('oslc_rm', OSLC_RM_JAZZ, override=True)
        graph.bind('oslc_cm', OSLC_CM_JAZZ, override=True)
        graph.bind('oslc_config', OSLC_CONFIG)
        graph.bind('jfs', JFS)
        graph.bind('trs', OSLC_TRS)

        test_url = url_for('oslc.adapter_service_provider_catalog', _external=True)

        # rs.add(OSLC_AM.amServiceProviders, URIRef(test_url))
        rs.add(OSLC_RM_JAZZ.rmServiceProviders, URIRef(test_url))
        # rs.add(OSLC_CM_JAZZ.cmServiceProviders, URIRef(test_url))
        # rs.add(OSLC_CONFIG.cmServiceProviders, URIRef(test_url))

        rs.add(JFS.oauthRealmName, Literal("PyOSLC"))
        rs.add(JFS.oauthDomain, Literal(url_for('web.index', _external=True)))
        rs.add(JFS.oauthRequestConsumerKeyUrl, URIRef(url_for('consumer.register', _external=True)))
        rs.add(JFS.oauthApprovalModuleUrl, URIRef(url_for('consumer.approve', _external=True)))
        rs.add(JFS.oauthRequestTokenUrl, URIRef(url_for('oauth.issue_token', _external=True)))
        rs.add(JFS.oauthUserAuthorizationUrl, URIRef(url_for('oauth.issue_token', _external=True)))
        rs.add(JFS.oauthAccessTokenUrl, URIRef(url_for('oauth.issue_token', _external=True)))

        pyoslc = Namespace('http://example.com/ns/pyoslc#')
        graph.bind('pyoslc', pyoslc)

        trs = Resource(graph, BNode())
        trs.add(RDF.type, pyoslc.TrackedResourceSetProvider)

        trs_url = URIRef(url_for('web.index', _external=True))

        tr = Resource(graph, BNode())
        tr.add(RDF.type, OSLC_TRS.TrackedResourceSet)
        tr.add(OSLC_TRS.trackedResourceSet, URIRef(trs_url))

        # # trs.add(RDF.type, OSLC_TRS.TrackedResourceSet)
        # # trs.add(DCTERMS.title, Literal('Title', datatype=XSD.Literal))
        tr.add(DCTERMS.title, Literal('Title'))
        tr.add(DCTERMS.description, Literal('Description'))
        # # trs.add(OSLC_TRS.trackedResourceSet, URIRef(url_for('web.index', _external=True)))

        tr.add(DCTERMS.type, OSLC_CM.uri)
        tr.add(OSLCCore.domain, OSLC_RM.uri)
        tr.add(OSLCCore.domain, OSLC_AM.uri)

        trs.add(OSLC_TRS.TrackedResourceSet, tr)
        rs.add(pyoslc.TrackedResourceSetProvider, trs)

        return rs
