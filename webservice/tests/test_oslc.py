

def test_requirement(client, oslc):
    # Testing Web
    headers = {
        'Content-Type': 'application/json-ld',
        'Accept': 'application/json-ld'
    }
    assert client.get('oslc/rm/requirement', headers=headers).status_code == 200

    response = client.get('/')
    assert b"PyOSLC" in response.data
    assert b"Service Provider Catalog" in response.data
    assert b'href="/api/1/catalog"' in response.data

    # Testing REST
    response = oslc.catalog()
    assert b'http://examples.org/oslc/catalog/serviceProvider' in response.data

