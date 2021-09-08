from collections import namedtuple

ResourceRoute = namedtuple("ResourceRoute", "resource urls kwargs")


class Namespace(object):

    def __init__(self, api, title, description, path='/', authorizations=None, **kwargs):
        self.api = api
        self.title = title
        self.description = description
        self._path = path
        self.resources = []  # List[ResourceRoute]
        self.authorizations = authorizations

    @property
    def path(self):
        return (self._path or ("/" + self.title)).rstrip("/")

    def add_resource(self, resource, *urls, **kwargs):
        self.resources.append(ResourceRoute(resource, urls, kwargs))
        if self.api is not None:
            ns_urls = self.api.ns_urls(self, urls)
            self.api.register_resource(self, resource, *ns_urls, **kwargs)
