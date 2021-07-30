def test_index(pyoslc):
    """
    GIVEN The PyOSLC API
    WHEN retrieving the root path
    THEN it should return the home page with the links to
         the swagger application with the /oslc path
    """
    response = pyoslc.get_swagger()
    assert b"PyOSLC" in response.data
    assert b"An OSLC adapter implemented on Python." in response.data
    assert b"For showing the REST API implementation for the OSLC adapter click the next button." in response.data
    assert b'href="/"' in response.data
    assert b'href="/oslc/"' in response.data


def test_oslc(pyoslc):
    """
    GIVEN The PyOSLC API that includes the swagger library
    WHEN requesting the oslc path
    THEN the swagger.json elements should be validated
    """
    response = pyoslc.get_swagger('/oslc/')
    assert response.status_code == 200
    assert b'swagger.json' in response.data


def test_list_requirement(client):
    """
    Testing the feature for listing of the requirements
    showed on the page
    """
    headers = {
        'Content-Type': 'text/html',
        'Accept': 'text/html'
    }
    response = client.get('oslc/rm/requirement', headers=headers)
    assert b'Listing the Requirements.' in response.data
    assert b'http://localhost/oslc/rm/requirement/X1C2V3B4' in response.data


def test_requirement(client):
    """
    Testing the information showed for a specific requirement
    """
    headers = {
        'Content-Type': 'text/html',
        'Accept': 'text/html'
    }
    response = client.get('oslc/rm/requirement/X1C2V3B4', headers=headers)
    assert b'http://purl.org/dc/terms/identifier' in response.data
    assert b'X1C2V3B4' in response.data
    assert b'http://purl.org/dc/terms/title' in response.data
    assert b'OSLC RM Spec 4' in response.data
    assert b'http://open-services.net/ns/core#shortTitle' in response.data
    assert b'SDK-Dev' in response.data
    assert b'http://purl.org/dc/terms/subject' in response.data
    assert b'OSLC RM Spec 4' in response.data
    assert b'http://purl.org/dc/terms/description' in response.data
    assert b'The OSLC RM Specification needs to be awesome 4' in response.data
    assert b'http://open-services.net/ns/rm#constrainedBy' in response.data
    assert b'Customer Requirement' in response.data
    assert b'http://open-services.net/ns/rm#satisfiedBy' in response.data
    assert b'Software Development' in response.data
