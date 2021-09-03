_service_resources = {}


class ServiceResourceException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)
        self.msg = msg


class ServiceResourceDescription(object):

    def __init__(self, name, kind, module_path, class_name):
        self.name = name
        self.kind = kind
        self.module_path = module_path
        self.class_name = class_name
        self._class = None

    def get_class(self):
        if self._class is None:
            module = __import__(self.module_path, globals(), locals(), [""])
            self._class = getattr(module, self.class_name)
        return self._class


def config_service_resource(name, kind, module_path, class_name):
    srd = ServiceResourceDescription(name, kind, module_path, class_name)
    _service_resources[(name, kind)] = srd


def get_service_resources(key, kind):
    try:
        rs = [_service_resources[r] for r in _service_resources if r[1] == kind and r[0] == key]
    except KeyError:
        raise ServiceResourceException(
            "No Service Resource registered for (%s)" % kind)
    return [r.get_class() for r in rs]
