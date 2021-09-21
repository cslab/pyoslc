
class Requirement:

    identifier = ""
    title = ""
    description = ""

    def __init__(self, identifier, title, description):
        self.identifier = identifier
        self.title = title
        self.description = description


REQSTORE = [
    Requirement("1", "Provide WSGI implementation", "..."),
    Requirement("2", "Capability to add resources", "..."),
    Requirement("3", "Capability to paging", "..."),
    Requirement("4", "Capability to select page", "..."),
    Requirement("5", "Capability to specify page size", "..."),
    # and so on ...
]
