from pyoslc.resources.models import ServiceProvider


def test_service_provider():
    sp = ServiceProvider()

    assert sp is not None
