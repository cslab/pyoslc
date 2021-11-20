import six

from pyoslc.resources.models import ServiceProvider


def test_service_provider():
    sp = ServiceProvider(title=u"Service Provider")

    assert sp is not None
    assert isinstance(sp.title, six.text_type)
