import json


def test_list_requirement(oslc):
    """
    Testing the REST API for listing the requirements
    taking the synthetic data from the CSV file
    """
    response = oslc.list()
    assert b'http://localhost/oslc/rm/requirement/X1C2V3B1' in response.data
    assert b'http://localhost/oslc/rm/requirement/X1C2V3B2' in response.data
    assert b'http://localhost/oslc/rm/requirement/X1C2V3B3' in response.data
    assert b'http://localhost/oslc/rm/requirement/X1C2V3B4' in response.data
    assert b'http://localhost/oslc/rm/requirement/X1C2V3B5' in response.data


def test_item_requirement(oslc):
    """
    Retrieving the information for a specific requirement
    using the oslc client and passing the id as a parameter
    """
    response = oslc.item('X1C2V3B1')
    assert b'http://localhost/oslc/rm/requirement/X1C2V3B1' in response.data
    assert b'http://purl.org/dc/terms/shortTitle' in response.data
    assert b'OSLC SDK 1' in response.data
    assert b'http://purl.org/dc/terms/subject' in response.data
    assert b'OSLC-Project 1' in response.data
    assert b'http://purl.org/dc/terms/title' in response.data
    assert b'OSLC RM Spec 1' in response.data


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
    assert response.data == '{}'
