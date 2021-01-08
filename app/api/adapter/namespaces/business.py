import csv
import os
import shutil
from tempfile import NamedTemporaryFile

from app.api.adapter.mappings.specification import specification_map
from pyoslc.resources.domains.rm import Requirement

attributes = specification_map


def get_requirement(base_url, specification_id):
    path = 'examples/specifications.csv'
    if os.path.isfile(path):
        with open(path, 'r') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row['Specification_id'] == specification_id:
                    about = base_url.replace('selector', 'requirement')
                    requirement = Requirement(about=about)
                    requirement.update(row, attributes)

                    return requirement


def get_requirement_list(base_url, select, where):
    requirements = list()
    path = 'examples/specifications.csv'
    if os.path.isfile(path):
        with open(path, 'r') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                requirement = Requirement()
                requirement.update(row, attributes=attributes)
                requirements.append(requirement)

    return requirements


def get_requirements(base_url):
    path = 'examples/specifications.csv'
    requirements = list()
    with open(path, 'r') as f:
        reader = csv.DictReader(f, delimiter=';')

        for row in reader:
            about = base_url.replace('selector', 'requirement') + '/' + row['Specification_id']
            requirement = Requirement(about=about)
            requirement.update(row, attributes=attributes)
            requirements.append(requirement)

    return requirements


def create_requirement(data):
    if data:
        requirement = Requirement()
        requirement.from_json(data=data, attributes=attributes)
        specification = requirement.to_mapped_object(attributes)

        path = os.path.join(os.path.abspath(''), 'examples', 'specifications.csv')
        tempfile = NamedTemporaryFile(mode='w', delete=False)

        with open(path, 'rb') as f:
            reader = csv.DictReader(f, delimiter=';')
            field_names = reader.fieldnames

        with open(path, 'r') as csvfile, tempfile:
            reader = csv.DictReader(csvfile, fieldnames=field_names, delimiter=';')
            writer = csv.DictWriter(tempfile, fieldnames=field_names, delimiter=';')
            exist = False

            for row in reader:
                if row['Specification_id'] == specification['Specification_id']:
                    exist = True
                writer.writerow(row)

            if not exist:
                writer.writerow(specification)

        shutil.move(tempfile.name, path)

        if exist:
            response_object = {
                'status': 'fail',
                'message': 'Not Modified'
            }
            return response_object, 304

        return requirement


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
