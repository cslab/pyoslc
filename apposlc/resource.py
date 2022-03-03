# -*- coding: utf-8 -*-
class Requirement:

    identifier = ""
    title = ""
    description = ""
    creator = ""

    def __init__(self, identifier, title, description, creator):
        self.identifier = identifier
        self.title = title
        self.description = description
        self.creator = creator


REQSTORE = [
    Requirement("1", "Provide WSGI implementation", "...", "Yi"),
    Requirement("2", "Capability to add resources", "...", "Jörg"),
    Requirement("3", "Capability to paging", "...", "Christian"),
    Requirement("4", "Capability to select page", "...", "Arne"),
    Requirement("5", "Capability to specify page size", "...", "Torben"),
    # and so on ...
]
