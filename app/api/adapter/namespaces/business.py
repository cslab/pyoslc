import csv
import os
import shutil
from tempfile import NamedTemporaryFile

from rdflib import Graph, DCTERMS
from werkzeug.exceptions import NotFound

from app.api.adapter.exceptions import NotModified
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
        if isinstance(data, Graph):
            requirement.from_rdf(data, attributes=attributes)
            identifier = [(s, o) for s, o in data.subject_objects(DCTERMS.identifier)][0]
            if identifier:
                requirement.identifier = identifier[1]
                requirement.about = identifier[0]
        else:
            requirement.from_json(data=data, attributes=attributes)

        specification = requirement.to_mapped_object(attributes)

        if specification:
            path = 'examples/specifications.csv'
            tempfile = NamedTemporaryFile(mode='w', delete=False)

            with open(path, 'r') as f:
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
                return NotModified()

            return requirement

        else:
            return NotFound()


def update_requirement(requirement_id, data):
    if data:
        requirement = Requirement()
        if isinstance(data, Graph):
            requirement.from_rdf(data, attributes=attributes)
            identifier = [(s, o) for s, o in data.subject_objects(DCTERMS.identifier)][0]
            if identifier:
                requirement.identifier = identifier[1]
                requirement.about = identifier[0]
        else:
            requirement.from_json(data=data, attributes=attributes)

        specification = requirement.to_mapped_object(attributes)

        if specification:
            path = 'examples/specifications.csv'
            tempfile = NamedTemporaryFile(mode='w', delete=False)

            with open(path, 'r') as f:
                reader = csv.DictReader(f, delimiter=';')
                field_names = reader.fieldnames

            modified = False
            with open(path, 'r') as csvfile, tempfile:
                reader = csv.DictReader(csvfile, fieldnames=field_names, delimiter=';')
                writer = csv.DictWriter(tempfile, fieldnames=field_names, delimiter=';')
                for row in reader:
                    if row['Specification_id'] == str(requirement_id):
                        rq = Requirement()
                        rq.from_json(specification, attributes=attributes)
                        row = rq.to_mapped_object(attributes=attributes)
                        row['Specification_id'] = requirement_id
                        modified = True
                    writer.writerow(row)

            shutil.move(tempfile.name, path)

            if not modified:
                raise NotModified()

            return requirement

        else:
            return NotFound()


def delete_requirement(requirement_id):
    path = 'examples/specifications.csv'
    tempfile = NamedTemporaryFile(mode='w', delete=False)

    with open(path, 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        field_names = reader.fieldnames

    modified = False
    with open(path, 'r') as csvfile, tempfile:
        reader = csv.DictReader(csvfile, fieldnames=field_names, delimiter=';')
        writer = csv.DictWriter(tempfile, fieldnames=field_names, delimiter=';')
        for row in reader:
            if row['Specification_id'] != str(requirement_id):
                writer.writerow(row)
            else:
                modified = True

    shutil.move(tempfile.name, path)

    if not modified:
        return NotModified()

    return True


def get_field_names(path):
    with open(path, 'rb') as f:
        reader = csv.DictReader(f, delimiter=';')
        field_names = reader.fieldnames
    return field_names if field_names else None


def update_store(id, data):
    pass
