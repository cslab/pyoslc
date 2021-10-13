from collections import namedtuple

ResourceRoute = namedtuple("ResourceRoute", "resource urls kwargs")


class Namespace(object):

    def __init__(self, api, title, description, path='/', authorizations=None, **kwargs):
        self.api = api
        self.title = title
        self.description = description
        self._path = path
        self.resources = []
        self.adapters = set()
        self.authorizations = authorizations

    @property
    def path(self):
        return (self._path or ("/" + self.title)).rstrip("/")

    def add_resource(self, resource, adapter, *urls, **kwargs):
        r = ResourceRoute(resource, urls, kwargs)
        if r not in self.resources:
            self.api.app.logger.debug(
                "Adding Resource: <resource: {resource}> <namespace: {namespace}> <adapter: {adapter}>".format(
                    resource=resource.__name__, namespace=self.title,
                    adapter=adapter)
            )
            self.resources.append(ResourceRoute(resource, urls, kwargs))
            if self.api is not None:
                ns_urls = self.api.ns_urls(self, urls)
                self.api.register_resource(self, resource, *ns_urls, **kwargs)

    def add_adapter(self, adapter):
        if adapter:
            self.adapters.add(adapter)
