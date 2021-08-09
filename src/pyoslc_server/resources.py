from collections import namedtuple

ResourceRoute = namedtuple("ResourceRoute", "resource urls route_doc kwargs")


class ServiceProviderResource(object):

    def __init__(self, name, description, authorizations=None,):
        self.name = name
        self.description = description
        self.resources = []  # List[ResourceRoute]
        self.authorizations = authorizations

