import json
import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.skip(reason="Migrating to OSLCAPP")
def test_get_list_requirement(pyoslc):
    """
    Testing the REST API for listing the requirements
    taking the synthetic data from the CSV file
    """
    response = pyoslc.list()
    assert b'http://localhost/oslc/rm/requirement/X1C2V3B1' in response.data
    assert b'http://localhost/oslc/rm/requirement/X1C2V3B2' in response.data
    assert b'http://localhost/oslc/rm/requirement/X1C2V3B3' in response.data
    assert b'http://localhost/oslc/rm/requirement/X1C2V3B4' in response.data
    assert b'http://localhost/oslc/rm/requirement/X1C2V3B5' in response.data


@pytest.mark.skip(reason="Migrating to OSLCAPP")
def test_get_item_requirement(pyoslc):
    """
    Retrieving the information for a specific requirement
    using the oslc client and passing the id as a parameter
    """
    response = pyoslc.item('X1C2V3B1')
    assert b'http://localhost/oslc/rm/requirement/X1C2V3B1' in response.data
    assert b'http://open-services.net/ns/core#shortTitle' in response.data
    assert b'SDK-Dev' in response.data
    assert b'http://purl.org/dc/terms/subject' in response.data
    assert b'Project-1' in response.data
    assert b'http://purl.org/dc/terms/title' in response.data
    assert b'The ACRV shall provide medical life-support accommodations for one crew member' in response.data


@pytest.mark.skip(reason="Migrating to OSLCAPP")
def test_insert_requirement(client):
    """
    Testing the method for posting information
    to insert a requirement on the csv file (synthetic data)
    """
    specification = dict(specification_id='X1C2V3B7',
                         product='OSLC SDK 7',
                         project='OSLC-Project 7',
                         title='OSLC RM Spec 7',
                         description='The OSLC RM Specification needs to be awesome 7',
                         source='Ian Altman',
                         author='Frank',
                         category='Customer Requirement',
                         discipline='Software Development',
                         revision='0',
                         target_value='1',
                         degree_of_fulfillment='0',
                         status='Draft')
    response = client.post('oslc/rm/requirement',
                           data=json.dumps(specification),
                           content_type='application/json')
    assert response.status_code == 201
    assert response.data == b''

    response = client.delete('oslc/rm/requirement/X1C2V3B7',
                             content_type='application/json')
    assert response.status_code == 200


@pytest.mark.skip(reason="Migrating to OSLCAPP")
def test_update_requirement(client):
    """
    Testing the method for sending the specification
    with some changes on the information of the
    specification inserted previously
    """

    specification = dict(specification_id='X1C2V3B7',
                         product='OSLC SDK 7',
                         project='OSLC-Project 7',
                         title='OSLC RM Spec 7',
                         description='The OSLC RM Specification needs to be awesome 7',
                         source='Ian Altman',
                         author='Frank',
                         category='Customer Requirement',
                         discipline='Software Development',
                         revision='0',
                         target_value='1',
                         degree_of_fulfillment='0',
                         status='Draft')
    response = client.post('oslc/rm/requirement',
                           data=json.dumps(specification),
                           content_type='application/json')
    assert response.status_code == 201
    assert response.data == b''

    specification = dict(specification_id='X1C2V3B7',
                         product='OSLC SDK 7 updated',
                         project='OSLC-Project 7 updated',
                         title='OSLC RM Spec 7 updated',
                         description='The OSLC RM Specification needs to be awesome 7 updated',
                         source='Ian Altman',
                         author='Frank',
                         category='Customer Requirement',
                         discipline='Software Development',
                         revision='0',
                         target_value='1',
                         degree_of_fulfillment='0',
                         status='Draft')
    response = client.put('oslc/rm/requirement/X1C2V3B7',
                          data=json.dumps(specification),
                          content_type='application/json')
    assert response.status_code == 200
    assert response.data != b''

    response = client.delete('oslc/rm/requirement/X1C2V3B7',
                             content_type='application/json')
    assert response.status_code == 200


@pytest.mark.skip(reason="Migrating to OSLCAPP")
def test_update_not_modified_requirement(client):
    """
    Testing the method for sending the specification
    with some changes but with an non-existent id
    """
    specification = dict(specification_id='X1C2V3B7',
                         product='OSLC SDK 7',
                         project='OSLC-Project 7',
                         title='OSLC RM Spec 7',
                         description='The OSLC RM Specification needs to be awesome 7',
                         source='Ian Altman',
                         author='Frank',
                         category='Customer Requirement',
                         discipline='Software Development',
                         revision='0',
                         target_value='1',
                         degree_of_fulfillment='0',
                         status='Draft')
    response = client.post('oslc/rm/requirement',
                           data=json.dumps(specification),
                           content_type='application/json')
    assert response.status_code == 201
    assert response.data == b''

    specification = dict(specification_id='X1C2V3B7',
                         product='OSLC SDK 7 updated',
                         project='OSLC-Project 7 updated',
                         title='OSLC RM Spec 7 updated',
                         description='The OSLC RM Specification needs to be awesome 7 updated',
                         source='Ian Altman',
                         author='Frank',
                         category='Customer Requirement',
                         discipline='Software Development',
                         revision='0',
                         target_value='1',
                         degree_of_fulfillment='0',
                         status='Draft')
    response = client.put('oslc/rm/requirement/X1C2V3B7',
                          data=json.dumps(specification),
                          content_type='application/json')
    assert response.status_code == 200
    assert response.data != b''

    response = client.delete('oslc/rm/requirement/X1C2V3B7',
                             content_type='application/json')
    assert response.status_code == 200


@pytest.mark.skip(reason="Migrating to OSLCAPP")
def test_delete_requirement(client):
    """
    Testing the method for deleting requirements from the store
    sending a non-existent id
    """

    specification = dict(specification_id='X1C2V3B7',
                         product='OSLC SDK 7',
                         project='OSLC-Project 7',
                         title='OSLC RM Spec 7',
                         description='The OSLC RM Specification needs to be awesome 7',
                         source='Ian Altman',
                         author='Frank',
                         category='Customer Requirement',
                         discipline='Software Development',
                         revision='0',
                         target_value='1',
                         degree_of_fulfillment='0',
                         status='Draft')
    response = client.post('oslc/rm/requirement',
                           data=json.dumps(specification),
                           content_type='application/json')
    logger.debug(response)
    assert response.status_code == 201

    response = client.delete('oslc/rm/requirement/X1C2V3B7',
                             content_type='application/json')
    assert response.status_code == 200


@pytest.mark.skip(reason="Migrating to OSLCAPP")
def test_delete_not_modified_requirement(client):
    response = client.delete('oslc/rm/requirement/X1C2V3B8',
                             content_type='application/json')
    assert response.status_code == 304
    assert response.data == b''
