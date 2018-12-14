"""
    This is a test module for the pyoslc project.
"""
from pyoslc.oslc import PyOSLC
from pyoslc.resource import ServiceProviderCatalog

# spc = ServiceProviderCatalog()
# data = spc.to_rdf(format='turtle')
# print(data.decode('utf-8'))
from pyoslc.vocabulary import OSLCCore

pyoslc = PyOSLC()


@pyoslc.oslc_service(resource_type=OSLCCore.serviceProviderCatalog,
                     about='catalog')
def catalog(name, age):

    return {
        'name': name,
        'age': age
    }


print(catalog('mario', 39))