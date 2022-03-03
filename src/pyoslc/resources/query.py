import re
import logging

from pyoslc.resources.ebnf_grammar import TERM, VALUE, PROPERTY, PREFIX_DEF

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Property(object):

    def __init__(self, prop, props=None):
        self.__prop = prop
        self.__props = props if props else []

    @property
    def prop(self):
        return self.__prop

    @property
    def props(self):
        return self.__props


class Condition(Property):

    def __init__(self, prop, nested_terms=None, operator=None, values=None):
        super(Condition, self).__init__(prop, nested_terms)
        self.__operator = operator
        self.__values = values
        self.scoped = True if nested_terms else False

    @property
    def operator(self):
        return self.__operator

    @property
    def values(self):
        return self.__values


class Criteria:

    def __init__(self):
        self.__prefixes = dict()
        self.__conditions = list()
        self.__properties = list()

    @property
    def conditions(self):
        return self.__conditions

    @conditions.setter
    def conditions(self, conditions):
        self.__conditions = conditions

    @property
    def properties(self):
        return self.__properties

    @properties.setter
    def properties(self, properties):
        self.__properties = properties

    @property
    def prefixes(self):
        return self.__prefixes

    @prefixes.setter
    def prefixes(self, prefixes):
        self.__prefixes = prefixes

    def in_val(self, val):
        values = list()
        if not re.search((VALUE + "(," + VALUE + ")*"), val):
            raise ValueError("Bad formed val: " + val)

        pattern = re.compile(",?" + VALUE)
        matchers = pattern.finditer(val)

        for matcher in matchers:
            values.append(matcher.group(1))

        return values

    def compound_term(self, compound_term):
        if not compound_term or compound_term == '':
            local_conditions = list()
        elif not re.search(TERM + "( and " + TERM + ")*", compound_term):
            raise ValueError("Bad formed where {where} on compound_term".format(where=compound_term))
        else:
            local_conditions = list()
            pattern = re.compile("( and )?" + TERM)
            matchers = pattern.finditer(compound_term)

            for matcher in matchers:
                prop = matcher.group(2)
                prop = self.qualified_name(prop)
                if matcher.group(23):
                    local_conditions.append(
                        Condition(prop=prop, nested_terms=self.compound_term(matcher.group(23)))
                    )
                elif matcher.group(19):
                    local_conditions.append(
                        Condition(prop=prop, operator=matcher.group(19), values=self.in_val(matcher.group(20)))
                    )
                else:
                    local_conditions.append(
                        Condition(prop=prop, operator=matcher.group(7), values=matcher.group(9))
                    )

        return local_conditions

    def props(self, parameter):
        if not parameter or parameter == '':
            local_properties = list()
        elif not re.search(PROPERTY + "(," + PROPERTY + ")*", parameter):
            raise ValueError("Bad formed properties: " + parameter)
        else:
            local_properties = list()
            pattern = re.compile(",?" + PROPERTY)
            matchers = pattern.finditer(parameter)

            for matcher in matchers:
                prop = matcher.group(1)
                prop = self.qualified_name(prop)
                if matcher.group(6) is None:
                    local_properties.append(Property(prop))
                else:
                    local_properties.append(Property(prop, self.props(matcher.group(6))))

        return local_properties

    def prefix(self, parameter):
        if not parameter or parameter == '':
            prfxs = dict()
        elif not re.search(PREFIX_DEF + "(," + PREFIX_DEF + ")*", parameter):
            raise ValueError("Bad formed oslc.prefix: " + parameter)
        else:
            prfxs = dict()
            pattern = re.compile(",?" + PREFIX_DEF)
            matchers = pattern.finditer(parameter)

            for matcher in matchers:
                prfxs.update({matcher.group(1): matcher.group(3)})
                # logger.debug("[+] PREFIX {}=<{}>".format(matcher.group(1), matcher.group(3)))

        self.__prefixes = prfxs

    def where(self, parameter):
        """
        v2: https://archive.open-services.net/bin/view/Main/OSLCCoreSpecQuery.html#oslc_where
        v3: https://docs.oasis-open-projects.org/oslc-op/query/v3.0/os/oslc-query.html#oslc.where
        """
        self.conditions = self.compound_term(parameter)

    def select(self, parameter):
        self.properties = self.props(parameter)

    def qualified_name(self, parameter):
        prefix = parameter.split(':')[0]
        ns = self.prefixes.get(prefix, 'http://example.com/')
        return ns + parameter.split(':')[1]


if __name__ == "__main__":
    # txt = "cm:severity in [\"high\",\"medium\"]"
    # txt = "qm:testcase=<http://example.com/tests/31459>"

    prfx = "foaf=<http://xmlns.com/foaf/0.1/>,cm=<http://open-services.net/ns/cm#>,qm=<http://open-services.net/ns/qm#>"
    qry = "cm:severity in [\"high\",\"medium\"] and qm:testcase=<http://example.com/tests/31459>"
    slct = "dcterms:created,dcterms:creator{foaf:familyName}"

    criteria = Criteria()
    criteria.prefix(prfx)
    criteria.where(qry)
    criteria.select(slct)
    print(criteria)
