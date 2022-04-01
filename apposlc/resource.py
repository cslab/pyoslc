# -*- coding: utf-8 -*-
class Creator:

    identifier = ""
    first_name = ""
    last_name = ""
    birth_day = ""

    def __init__(self, identifier, first_name, last_name):
        self.identifier = identifier
        self.first_name = first_name
        self.last_name = last_name


CREATORSTORE = [
    Creator("1", "Yi", "Chen"),
    Creator("2", "Jörg", "Kollman"),
    Creator("3", "Christian", "Muggeo"),
    Creator("4", "Arne", "Kiel"),
    Creator("5", "Torben", "Hansing"),
    Creator("6", "Ian", "Altman"),
    Creator("7", "Frank", "Patz-Brockmann"),
]


class Requirement:

    identifier = ""
    title = ""
    description = ""
    creator = None

    def __init__(self, identifier, title, description, creator):
        self.identifier = identifier
        self.title = title
        self.description = description
        self.creator = creator


REQSTORE = [
    Requirement("1", "Provide WSGI implementation", "...", CREATORSTORE[0]),  # how to manage the linkage
    Requirement("2", "Capability to add resources", "...", CREATORSTORE[1]),
    Requirement("3", "Capability to paging", "...", CREATORSTORE[2]),
    Requirement("4", "Capability to select page", "...", CREATORSTORE[3]),
    Requirement("5", "Capability to specify page size", "...", CREATORSTORE[4]),
    # and so on ...
]
