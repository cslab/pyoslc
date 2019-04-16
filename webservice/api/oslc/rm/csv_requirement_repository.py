import csv
import os

from webservice.api.oslc.adapter.repository import Repository
from pyoslc.resources.requirement import Requirement


class CsvRequirementRepository(Repository):

    specification_map = {
        'Specification_id': {'attribute': '_Resource___identifier', 'oslc_property': 'DCTERMS.identifier'},
        'Product': {'attribute': '_Resource___short_title', 'oslc_property': 'DCTERMS.shortTitle'},
        'Project': {'attribute': '_Resource___subject', 'oslc_property': 'DCTERMS.subject'},
        'Title': {'attribute': '_Resource___title', 'oslc_property': 'DCTERMS.title'},
        'Description': {'attribute': '_Resource___description', 'oslc_property': 'DCTERMS.description'},
        'Source': {'attribute': '_Requirement__elaborated_by', 'oslc_property': 'OSLC_RM.elaboratedBy'},
        'Author': {'attribute': '_Resource___creator', 'oslc_property': 'DCTERMS.creator'},
        'Category': {'attribute': '_Requirement__constrained_by', 'oslc_property': 'OSLC_RM.constrainedBy'},
        'Discipline': {'attribute': '_Requirement__satisfied_by', 'oslc_property': 'OSLC_RM.satisfiedBy'},
        'Revision': {'attribute': '_Requirement__tracked_by', 'oslc_property': 'OSLC_RM.trackedBy'},
        'Target_Value': {'attribute': '_Requirement__validated_by', 'oslc_property': 'OSLC_RM.validatedBy'},
        'Degree_of_fulfillment': {'attribute': '_Requirement__affected_by', 'oslc_property': 'OSLC_RM.affectedBy'},
        'Status': {'attribute': '_Requirement__decomposed_by', 'oslc_property': 'OSLC_RM.decomposedBy'}
    }

    def __init__(self):
        # self.csv_file_path = csv_file_path
        self.csv_file_path = os.path.join(
            os.path.abspath(''), 'examples', 'specifications.csv')

    def create(self, requirement):
        with open(self.csv_file_path, 'a') as f:
            fieldnames = CsvRequirementRepository.specification_map.keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writerow(
                CsvRequirementRepository.requirement_to_dict(requirement))

    def read(self):
        with open(self.csv_file_path, 'rb') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                yield CsvRequirementRepository.read_requirement(row)

    def delete(self, requirement):
        temp_csv_file_path = 'temp_' + self.csv_file_path
        with open(self.csv_file_path, 'rb') as file, open(temp_csv_file_path, 'wb') as new_file:
            fieldnames = CsvRequirementRepository.specification_map.keys()
            writer = csv.DictWriter(
                new_file, fieldnames=fieldnames, delimiter=';')
            for row in csv.reader(file):
                if requirement.identifier != CsvRequirementRepository.read_requirement(row).identifier:
                    writer.writerow(row)

        os.remove(self.csv_file_path)
        os.rename(temp_csv_file_path, self.csv_file_path)

    def update(self, requirement):
        temp_csv_file_path = 'temp_' + self.csv_file_path
        with open(self.csv_file_path, 'rb') as file, open(temp_csv_file_path, 'wb') as new_file:
            fieldnames = CsvRequirementRepository.specification_map.keys()
            writer = csv.DictWriter(
                new_file, fieldnames=fieldnames, delimiter=';')
            for row in csv.reader(file):
                if requirement.identifier == CsvRequirementRepository.read_requirement(row).identifier:
                    writer.writerow(
                        CsvRequirementRepository.requirement_to_dict(requirement))
                else:
                    writer.writerow(row)

        os.remove(self.csv_file_path)
        os.rename(temp_csv_file_path, self.csv_file_path)

    @staticmethod
    def requirement_to_dict(requirement):
        specification = dict()

        for key in CsvRequirementRepository.specification_map:
            # print('{}'.format(key))

            attribute_name = CsvRequirementRepository.specification_map[key]['attribute']
            if hasattr(requirement, attribute_name):
                attribute_value = getattr(requirement, attribute_name)
                if attribute_value:
                    if isinstance(attribute_value, set):
                        specification[key] = attribute_value.pop()
                    else:
                        specification[key] = attribute_value

        return specification

    @staticmethod
    def read_requirement(data):
        requirement = Requirement()
        for k, v in data.items():
            if k in CsvRequirementRepository.specification_map:
                attribute = CsvRequirementRepository.specification_map[k]['attribute']
                if hasattr(requirement, attribute):
                    attr = getattr(requirement, attribute, None)
                    if isinstance(attr, set):
                        attr.add(v if v is not '' else 'Empty')
                    else:
                        setattr(requirement, attribute, v)


repository = CsvRequirementRepository()

for req in repository.get():
    print req
