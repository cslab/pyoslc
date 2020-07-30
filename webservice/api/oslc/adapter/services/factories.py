from rdflib import DCTERMS, RDF, RDFS

from pyoslc.model.factory import ServiceProviderFactory
from pyoslc.resource import PrefixDefinition
from pyoslc.vocabulary import OSLCCore
from pyoslc.vocabulary.am import OSLC_AM
from pyoslc.vocabulary.cm import OSLC_CM
from pyoslc.vocabulary.data import OSLCData
from pyoslc.vocabulary.rm import OSLC_RM
from webservice.api.oslc.adapter.specs import DataSpecsProjectA


class ContactServiceProviderFactory(object):

    @classmethod
    def create_provider(cls, base_uri, title, description, publisher, parameters):
        classes = [DataSpecsProjectA]
        sp = ServiceProviderFactory.create(base_uri,
                                           'project',
                                           title,
                                           description,
                                           publisher,
                                           classes,
                                           parameters)

        # sp.add_detail(base_uri)

        prefix_definitions = list()
        prefix_definitions.append(PrefixDefinition(prefix='dcterms', prefix_base=DCTERMS))
        prefix_definitions.append(PrefixDefinition(prefix='oslc', prefix_base=OSLCCore))
        prefix_definitions.append(PrefixDefinition(prefix='oslc_data', prefix_base=OSLCData))
        prefix_definitions.append(PrefixDefinition(prefix='rdf', prefix_base=RDF))
        prefix_definitions.append(PrefixDefinition(prefix='rdfs', prefix_base=RDFS))
        prefix_definitions.append(PrefixDefinition(prefix='oslc_am', prefix_base=OSLC_AM))
        prefix_definitions.append(PrefixDefinition(prefix='oslc_cm', prefix_base=OSLC_CM))
        prefix_definitions.append(PrefixDefinition(prefix='oslc_rm', prefix_base=OSLC_RM))

        sp.prefix_definition = prefix_definitions

        return sp
