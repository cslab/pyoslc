from rdflib import URIRef, RDF, Literal, BNode
from rdflib.namespace import DCTERMS, XSD
from rdflib.resource import Resource

from pyoslc.vocabulary.jazz import JAZZ_DISCOVERY
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
