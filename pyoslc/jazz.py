from flask import url_for
from rdflib import URIRef, RDF, Literal, BNode
from rdflib.namespace import DCTERMS, XSD
from rdflib.resource import Resource

from pyoslc.vocabulary.am import OSLC_AM
from pyoslc.vocabulary.cm import OSLC_CM
from pyoslc.vocabulary.config import OSLC_CONFIG
from pyoslc.vocabulary.jazz import JAZZ_DISCOVERY
from pyoslc.vocabulary.jfs import JFS
from pyoslc.vocabulary.rm import OSLC_RM
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

        rs = Resource(graph, URIRef(self.about))

        if self.title:
            rs.add(DCTERMS.title, Literal(self.title, datatype=XSD.Literal))

        if self.description:
            rs.add(DCTERMS.description, Literal(self.description, datatype=XSD.Literal))

        graph.bind('oslc_am', OSLC_AM)
        graph.bind('oslc_rm', OSLC_RM)
        graph.bind('oslc_cm', OSLC_CM)
        graph.bind('jfs', JFS)
        graph.bind('oslc_config', OSLC_CONFIG)

        rs.add(OSLC_AM.amServiceProviders, URIRef(url_for('oslc.adapter_service_provider_catalog')))
        rs.add(OSLC_RM.rmServiceProviders, URIRef(url_for('oslc.adapter_service_provider_catalog')))
        rs.add(OSLC_CM.cmServiceProviders, URIRef(url_for('oslc.adapter_service_provider_catalog')))
        rs.add(OSLC_CONFIG.cmServiceProviders, URIRef(url_for('oslc.adapter_service_provider_catalog')))

        rs.add(JFS.oauthRealmName, Literal("PyOSLC"))
        rs.add(JFS.oauthDomain, URIRef(url_for('oslc.adapter_service_provider_catalog')))
        rs.add(JFS.oauthRequestConsumerKeyUrl, URIRef(url_for('oauth.initiate_temporary_credential', _external=True)))
        rs.add(JFS.oauthApprovalModuleUrl, URIRef(url_for('oauth.approve_key', _external=True)))
        # rs.add(JFS.oauthRequestTokenUrl, URIRef(url_for('oauth.initiate_temporary_credential', _external=True)))
        # rs.add(JFS.oauthUserAuthorizationUrl, URIRef(url_for('oslc.adapter_service_provider_catalog')))
        # rs.add(JFS.oauthAccessTokenUrl, URIRef(url_for('oslc.adapter_service_provider_catalog')))

        # <!-- OAuth URLs for establishing server-to-server connections -->
        # 	<jfs: rdf:resource="http://192.168.1.66:8080/iotp/services/oauth/requestKey" />
        # 	<jfs: rdf:resource="http://192.168.1.66:8080/iotp/services/oauth/approveKey" />
        # 	<jfs: rdf:resource="http://192.168.1.66:8080/iotp/services/oauth/requestToken"/>
        # 	<jfs: rdf:resource="http://192.168.1.66:8080/iotp/services/oauth/authorize" />
        # 	<jfs: rdf:resource="http://192.168.1.66:8080/iotp/services/oauth/accessToken"/>fs
        #

        if self.friends:
            for f in self.friends:
                r = f.to_rdf(graph)
                rs.add(JAZZ_DISCOVERY.friends, r.identifier)

        return rs


class Friend(Resource_):

    def __init__(self, about=None, types=None, properties=None,
                 description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None,
                 root_service=None):
        """
        Initialize Root Service
        """

        Resource_.__init__(self, about=about, types=types, properties=properties, description=description,
                           identifier=identifier, short_title=short_title, title=title, contributor=contributor,
                           creator=creator, subject=subject, created=created, modified=modified, type=type,
                           discussed_by=discussed_by, instance_shape=instance_shape, service_provider=service_provider,
                           relation=relation)

        self.__root_service = root_service or list()

    @property
    def root_service(self):
        return self.__root_service

    @root_service.setter
    def root_service(self, root_service):
        self.__root_service = root_service

    def add_root_service(self, root_service):
        self.__root_service.append(root_service)

    def to_rdf(self, graph):
        if not self.about:
            raise Exception("The title is missing")

        friend = Resource(graph, BNode())
        friend.add(RDF.type, URIRef(JAZZ_DISCOVERY.Friend))

        if self.title:
            friend.add(DCTERMS.title, Literal(self.title))

        if self.root_service:
            friend.add(JAZZ_DISCOVERY.rootServices, URIRef(self.root_service))

        return friend
