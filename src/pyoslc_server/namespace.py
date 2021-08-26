from collections import namedtuple

ResourceRoute = namedtuple("ResourceRoute", "resource urls kwargs")


class Namespace(object):

    def __init__(self, name, description=None, path='/', authorizations=None, **kwargs):
        self.name = name
        self.description = description
        self._path = path

        self.models = {}
        self.urls = {}
        self.resources = []  # List[ResourceRoute]
        self.authorizations = authorizations

        self.apis = []
        if "api" in kwargs:
            api = kwargs["api"]
            api.app.logger.debug(
                "Initializing Namespace <name: {name}> <path: {path}>".format(
                    name=name, description=description, path=path, kwargs=kwargs))
            self.apis.append(api)

    @property
    def path(self):
        return (self._path or ("/" + self.name)).rstrip("/")

    def add_resource(self, resource, *urls, **kwargs):
        self.resources.append(ResourceRoute(resource, urls, kwargs))
        for api in self.apis:
            ns_urls = api.ns_urls(self, urls)
            api.app.logger.debug('<Resource: {resource}> <urls: {urls}>'.format(resource=resource.__name__, urls=urls))
            api.register_resource(self, resource, *ns_urls, **kwargs)
