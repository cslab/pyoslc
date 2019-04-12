import csv
import os

from rdflib import Graph
from rdflib.namespace import DCTERMS

from pyoslc.resources.requirement import Requirement
from pyoslc.vocabulary import OSLCCore
from pyoslc.vocabulary.rm import OSLC_RM


def get_requirement_list(base_url):
    path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')
    with open(path, 'rb') as f:
        reader = csv.DictReader(f, delimiter=';')

        graph = Graph()
        graph.bind('oslc', OSLCCore, override=False)
        graph.bind('dcterms', DCTERMS, override=False)
        graph.bind('oslc_rm', OSLC_RM, override=False)

        for row in reader:
            requirement = Requirement()
            requirement.update(row)

            graph += requirement.to_rdf(base_url)

    return graph if graph else None


