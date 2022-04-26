import six

from pyoslc.resources.models import BaseResource, ServiceProvider
from pyoslc_server.specification import ServiceResourceAdapter


def test_service_provider():
    sp = ServiceProvider(title="Service Provider")

    assert sp
    assert isinstance(sp.title, six.text_type)


def test_base_resource():
    resource = BaseResource()

    data = {
        "http://purl.org/dc/terms/identifier": "XWq21d",
        "http://purl.org/dc/terms/description": "Data object to be converted",
        "http://purl.org/dc/terms/title": "Item",
        "http://purl.org/dc/terms/creator": "Patz-Brockmann, Frank",
    }

    adapter = ServiceResourceAdapter(
        identifier="test_base_resource", title="testing update"
    )
    resource.update(data, adapter)

    assert resource.description == "Data object to be converted"
    assert resource.creator == "Patz-Brockmann, Frank"
