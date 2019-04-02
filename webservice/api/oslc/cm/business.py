import csv
import os

from pyoslc.resources.requirement import Requirement


def create_requirement(data):
    pass


def get_requirement(specification_id):
    path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')
    with open(path, 'rb') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['Specification_id'] == specification_id:
                return row


def update_requirement(id, data):

    if data:
        requirement = Requirement()
        requirement.from_json(data=data)
        specification = requirement.to_mapped_object()

        path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')
        field_names = get_field_names(path=path)
        if field_names:
            with open(path, 'a') as f:
                writer = csv.DictWriter(f, fieldnames=field_names, delimiter=';')
                writer.writerow(specification)


def get_field_names(path):
    with open(path, 'rb') as f:
        reader = csv.DictReader(f, delimiter=';')
        field_names = reader.fieldnames
    return field_names if field_names else None


def update_store(id, data):
    pass
