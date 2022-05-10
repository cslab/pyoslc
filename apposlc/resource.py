# -*- coding: utf-8 -*-
from datetime import datetime


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
    created = None
    creator = None
    discipline = None

    def __init__(
        self,
        identifier,
        title,
        description,
        created=None,
        creator=None,
    ):
        self.identifier = identifier
        self.title = title
        self.description = description
        self.created = created
        self.creator = creator
        self.discipline = [
            {
                "https://contact-software.com/ontologies/v1.0/plm#text": "Leistungsbedarf",
                "https://contact-software.com/ontologies/v1.0/plm#language": "de",
            },
            {
                "https://contact-software.com/ontologies/v1.0/plm#text": "Power Requirement",
                "https://contact-software.com/ontologies/v1.0/plm#language": "en",
            },
        ]


dt = "%Y-%m-%d"

REQSTORE = [
    Requirement(
        "1",
        "Provide WSGI implementation",
        "...",
        datetime(2020, 1, 1).strftime(dt),
        CREATORSTORE[0],
    ),
    Requirement(
        "2",
        "Capability to add resources",
        "...",
        datetime(2020, 2, 2).strftime(dt),
        CREATORSTORE[1:3],
    ),
    Requirement(
        "3",
        "Capability to paging",
        "...",
        datetime(2020, 3, 3).strftime(dt),
        CREATORSTORE[2:4],
    ),
    Requirement(
        "4",
        "Capability to select page",
        "...",
        datetime(2020, 4, 4).strftime(dt),
        CREATORSTORE[3:5],
    ),
    Requirement(
        "5",
        "Capability to specify page size",
        "...",
        datetime(2020, 5, 5).strftime(dt),
        CREATORSTORE[4:7],
    ),
    # and so on ...
]
