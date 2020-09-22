"""
    This is a test module for the pyoslc project.
"""
from pyoslc.oslc import PyOSLC

from pyoslc.vocabularies.core import OSLC

pyoslc = PyOSLC()


# @oslc_service_provider_catalog(resource_type=OSLCCore.serviceProviderCatalog, about='catalog')
@pyoslc.oslc_service(resource_type=OSLC.serviceProviderCatalog, about='catalog')
def catalog(name, age):
    return {
        'name': name,
        'age': age
    }

print((catalog('mario', 39)))
