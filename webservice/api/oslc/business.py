import csv
import os

from rdflib import Graph

from pyoslc.resources.requirement import Requirement


def get_requirement_list(base_url):
    path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')
    with open(path, 'rb') as f:
        reader = csv.DictReader(f, delimiter=';')

        graph = Graph()

        for row in reader:
            requirement = Requirement()
            requirement.update(row)

            graph += requirement.to_rdf(base_url)

    return graph


