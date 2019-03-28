from rdflib import Graph
from rdflib.extras.describer import Describer
from rdflib.namespace import DCTERMS

from pyoslc.resource import Resource
from pyoslc.vocabulary.rm import OSLC_RM


class Requirement(Resource):

    specification_map = {
        'Product': {'attribute': '_Resource__short_title', 'oslc_property': 'DCTERMS.shortTitle'},
        'Project': {'attribute': '_Resource__subject', 'oslc_property': 'DCTERMS.subject'},
        'Title': {'attribute': '_Resource__title', 'oslc_property': 'DCTERMS.title'},
        'Description': {'attribute': '_Resource__description', 'oslc_property': 'DCTERMS.description'},
        'Source': {'attribute': '_Requirement__elaborated_by', 'oslc_property': 'OSLC_RM.elaboratedBy'},
        'Author': {'attribute': '_Resource__creator', 'oslc_property': 'DCTERMS.creator'},  # 'creator',
        'Category': {'attribute': '_Resource__creator', 'oslc_property': 'DCTERMS.creator'},
        'Discipline': {'attribute': '_Resource__creator', 'oslc_property': 'DCTERMS.creator'},
        'Revision': {'attribute': '_Resource__creator', 'oslc_property': 'DCTERMS.creator'},
        'Target_Value': {'attribute': '_Resource__creator', 'oslc_property': 'DCTERMS.creator'},
        'Degree_of_fulfillment': {'attribute': '_Resource__creator', 'oslc_property': 'DCTERMS.creator'},
        'Status': {'attribute': '_Resource__creator', 'oslc_property': 'DCTERMS.creator'}
    }

    def __init__(self, about=None, types=None, properties=None,
                 description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None,
                 created=None, modified=None, type=None, discussed_by=None,
                 instance_shape=None, service_provider=None, relation=None,
                 elaborated_by=None, elaborates=None, specified_by=None, specifies=None,
                 affected_by=None, tracked_by=None, implemented_by=None, validated_by=None,
                 satisfied_by=None, satisfies=None, decomposed_by=None, decomposes=None,
                 constrained_by=None, constrains=None):

        Resource.__init__(self, about, types, properties,
                          description, identifier, short_title,
                          title, contributor, creator, subject,
                          created, modified, type, discussed_by,
                          instance_shape, service_provider, relation)

        self.__elaborated_by = elaborated_by if elaborated_by is not None else set()
        self.__elaborates = elaborates if elaborates is not None else set()
        self.__specified_by = specified_by if specified_by is not None else set()
        self.__specifies = specifies if specifies is not None else set()
        self.__affected_by = affected_by if affected_by is not None else set()
        self.__tracked_by = tracked_by if tracked_by is not None else set()
        self.__implemented_by = implemented_by if implemented_by is not None else set()
        self.__validated_by = validated_by if validated_by is not None else set()
        self.__satisfied_by = satisfied_by if satisfied_by is not None else set()
        self.__satisfies = satisfies if satisfies is not None else set()
        self.__decomposed_by = decomposed_by if decomposed_by is not None else set()
        self.__decomposes = decomposes if decomposes is not None else set()
        self.__constrained_by = constrained_by if constrained_by is not None else set()
        self.__constrains = constrains if constrains is not None else set()

    def update(self, data):
        for k, v in data.items():
            if k in self.specification_map:
                attribute = self.specification_map[k]['attribute']
                if hasattr(self, attribute):
                    attr = getattr(self, attribute, None)
                    if isinstance(attr, set):
                        attr.add(v if v is not '' else 'Empty')
                    else:
                        setattr(self, attribute, v)
                    print('{} {} {}'.format(attribute, attr, type(attr)))
                else:
                    print('{}'.format(attribute))



    @staticmethod
    def get_absolute_url(identifier):
        return "/requirement/" + identifier

    def to_rdf(self):

        print(self.__dict__.keys())

        ORG_URI = "http://example.org/"

        graph = Graph()
        graph.bind('dcterms', DCTERMS)
        graph.bind('oslc_rm', OSLC_RM)

        d = Describer(graph, base=ORG_URI)
        d.about(self.get_absolute_url('1') + '#requirement')
        d.rdftype(OSLC_RM.Requirement)

        for attribute_key in self.__dict__.keys():
            item = {attribute_key: v.values() for k, v in self.specification_map.iteritems() if v['attribute'] == attribute_key}

            if item.values() and attribute_key in item.values()[0]:

                predicate = eval(item.values()[0][1])
                attr = getattr(self, attribute_key)
                if isinstance(attr, set):
                    d.value(predicate, attr.pop())
                else:
                    d.value(predicate, getattr(self, attribute_key))

                print('{} {}'.format(attribute_key, predicate))
            else:
                print('{}'.format(attribute_key))

        return graph

