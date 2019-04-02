def test_index(client, oslc):
    response = client.get('/')
    assert b"PyOSLC" in response.data
    assert b"For showing the REST API implementation for the OSLC adapter click the next button." in response.data
    assert b'href="/oslc/rm/requirement"' in response.data

    response = oslc.catalog()
    assert b'http://examples.org/oslc/catalog/serviceProvider' in response.data
