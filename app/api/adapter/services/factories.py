from rdflib import DCTERMS, RDF, RDFS

from app.api.adapter.resources.resource_service import get_service_resources
from app.api.adapter.services.specification import ServiceResource
from app.api.adapter.services.specs import DataSpecsProjectA
from pyoslc.resources.factories import ServiceProviderFactory
from pyoslc.resources.models import PrefixDefinition
from pyoslc.vocabularies.am import OSLC_AM
from pyoslc.vocabularies.cm import OSLC_CM
from pyoslc.vocabularies.core import OSLC
from pyoslc.vocabularies.data import OSLCData
from pyoslc.vocabularies.rm import OSLC_RM


class ContactServiceProviderFactory(object):

    @classmethod
    def create_service_provider(cls, base_uri, title, description, publisher, parameters):
        classes = [DataSpecsProjectA]
        klasses = get_service_resources(ServiceResource)

        sp = ServiceProviderFactory.create_service_provider(base_uri,
                                                            'project',
                                                            title,
                                                            description,
                                                            publisher,
                                                            classes,
                                                            klasses,
                                                            parameters)

        sp.add_detail(base_uri)

        prefix_definitions = list()
        prefix_definitions.append(PrefixDefinition(prefix='dcterms', prefix_base=DCTERMS))
        prefix_definitions.append(PrefixDefinition(prefix='oslc', prefix_base=OSLC))
        prefix_definitions.append(PrefixDefinition(prefix='oslc_data', prefix_base=OSLCData))
        prefix_definitions.append(PrefixDefinition(prefix='rdf', prefix_base=RDF))
        prefix_definitions.append(PrefixDefinition(prefix='rdfs', prefix_base=RDFS))
        prefix_definitions.append(PrefixDefinition(prefix='oslc_am', prefix_base=OSLC_AM))
        prefix_definitions.append(PrefixDefinition(prefix='oslc_cm', prefix_base=OSLC_CM))
        prefix_definitions.append(PrefixDefinition(prefix='oslc_rm', prefix_base=OSLC_RM))

        sp.prefix_definition = prefix_definitions

        return sp
