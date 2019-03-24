def test_index(client, oslc):
    response = client.get('/')
    assert b"PyOSLC" in response.data
    assert b"Service Provider Catalog" in response.data
    assert b'href="/api/1/catalog"' in response.data

    response = oslc.catalog()
    assert b'http://examples.org/oslc/catalog/serviceProvider' in response.data
