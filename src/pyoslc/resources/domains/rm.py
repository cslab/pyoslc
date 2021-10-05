import logging

from rdflib import RDF, Literal, DCTERMS
from rdflib.extras.describer import Describer

from pyoslc.resources.models import BaseResource
from pyoslc.vocabularies.core import OSLC
from pyoslc.vocabularies.rm import OSLC_RM
import six

logger = logging.getLogger(__name__)


class Requirement(BaseResource):

    def __init__(self, about=None, types=None, properties=None, description=None, identifier=None, short_title=None,
                 title=None, contributor=None, creator=None, subject=None, created=None, modified=None, type=None,
                 discussed_by=None, instance_shape=None, service_provider=None, relation=None, elaborated_by=None,
                 elaborates=None, specified_by=None, specifies=None, affected_by=None, tracked_by=None,
                 implemented_by=None, validated_by=None, satisfied_by=None, satisfies=None, decomposed_by=None,
                 decomposes=None, constrained_by=None, constrains=None):

        super(Requirement, self).__init__(about, types, properties, description, identifier, short_title, title,
                                          contributor, creator, subject, created, modified, type, discussed_by,
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

    def update(self, data, attributes):
        assert attributes is not None, 'The mapping for attributes is required'
        for k, v in data.items():
            if k in attributes:
                attribute_name = attributes[k]['attribute']
                if hasattr(self, attribute_name):
                    attribute_value = getattr(self, attribute_name)
                    if isinstance(attribute_value, set):
                        attribute_value.clear()
                        attribute_value.add(data[k])
                    else:
                        setattr(self, attribute_name, data[k])

    @staticmethod
    def get_absolute_url(base_url, identifier):
        return base_url + "/" + identifier

    def to_rdf(self, graph, base_url=None, attributes=None):
        assert attributes is not None, 'The mapping for attributes is required'

        graph.bind('oslc_rm', OSLC_RM)
        graph.bind('oslc', OSLC)
        graph.bind('dcterms', DCTERMS)

        d = Describer(graph, base=base_url)
        identifier = getattr(self, 'identifier')
        if isinstance(identifier, Literal):
            identifier = identifier.value
        if identifier not in base_url.split('/'):
            base_url = self.get_absolute_url(base_url, identifier)

        d.about(base_url)
        d.rdftype(OSLC_RM.Requirement)

        for attribute_key in self.__dict__.keys():
            item = {k: v for k, v in six.iteritems(attributes) if attribute_key == k}

            if item and attribute_key in item.keys():
                predicate = eval(item.get(attribute_key))
                attr = getattr(self, attribute_key)
                if isinstance(attr, set):
                    if len(attr) > 0:
                        val = attr.pop()
                        if isinstance(val, Literal):
                            d.value(predicate, val.value)
                        else:
                            d.value(predicate, val)
                        attr.add(val)
                    else:
                        attr = getattr(self, attribute_key)
                        val = attr.pop()
                        d.value(predicate, val)
                elif isinstance(attr, Literal):
                    data = getattr(self, attribute_key)
                    d.value(predicate, data.value)
                else:
                    d.value(predicate, getattr(self, attribute_key))

        return graph

    def from_json(self, data, attributes):
        for key in six.iterkeys(data):
            item = {key: b for a, b in six.iteritems(attributes) if a.lower() == key.lower()}

            if item:
                attribute_name = item[key]['attribute']
                if hasattr(self, attribute_name):
                    attribute_value = getattr(self, attribute_name)
                    if isinstance(attribute_value, set):
                        attr = getattr(self, attribute_name)
                        attr.add(data[key])
                    else:
                        setattr(self, attribute_name, data[key])

    def from_rdf(self, g, attributes):

        for r in g.subjects(RDF.type, OSLC_RM.Requirement):

            setattr(self, '_AbstractResource__about', str(r))

            reviewed = list()

            for k, v in six.iteritems(attributes):
                reviewed.append(k)

                for i in g.objects(r, predicate=v):
                    attribute_name = k
                    if hasattr(self, attribute_name):
                        attribute_value = getattr(self, attribute_name)
                        if isinstance(attribute_value, set):
                            at = getattr(self, attribute_name)
                            if isinstance(i, Literal):
                                i = i.value
                            at.add(i)
                        elif isinstance(attribute_value, str):
                            if isinstance(i, Literal):
                                i = i.value
                            setattr(self, attribute_name, i if isinstance(i, str) else i.encode('utf-8'))
                        else:
                            if isinstance(i, Literal):
                                setattr(self, attribute_name, i.value)
                            else:
                                setattr(self, attribute_name, i)

            no_reviewed = [a.split('__')[1].lower() for a in self.__dict__.keys() if
                           a.split('__')[1].lower() not in reviewed]

            for attr in no_reviewed:
                item = {attr: v for k, v in six.iteritems(attributes) if k.lower() == attr.lower()}
                if item:
                    for i in g.objects(r, eval(item.get(attr)['oslc_property'])):
                        attribute_name = item.get(attr)['attribute']
                        if hasattr(self, attribute_name):
                            attribute_value = getattr(self, attribute_name)
                            if isinstance(attribute_value, set):
                                attribute_value.clear()
                                # attribute_value.add(data[key])
                            else:
                                setattr(self, attribute_name, i)

    def to_mapped_object(self, attributes):
        specification = dict()

        for key in attributes:
            attribute_name = attributes[key]['attribute']
            if hasattr(self, attribute_name):
                attribute_value = getattr(self, attribute_name)
                if attribute_value:
                    if isinstance(attribute_value, set):
                        val = attribute_value.pop()
                        if len(attribute_value) == 0:
                            specification[key] = val
                        else:
                            try:
                                attr = specification[key]
                            except KeyError:
                                specification[key] = set()
                                attr = specification[key]
                            attr.add(val)
                        attribute_value.add(val)
                    else:
                        if isinstance(attribute_value, Literal):
                            specification[key] = attribute_value.value
                        else:
                            specification[key] = attribute_value

        return specification


class RequirementCollection(BaseResource):
    pass
