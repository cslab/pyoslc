import xml

from rdflib import BNode, URIRef, RDFS, Literal, Namespace
from rdflib.collection import Collection
from rdflib.plugins.serializers.rdfxml import PrettyXMLSerializer, XMLBASE, fix, OWL_NS, XMLLANG
from rdflib.plugins.serializers.xmlwriter import XMLWriter
from rdflib.util import first, more_than
from six import b

from pyoslc.vocabularies.jazz import JAZZ_DISCOVERY, JAZZ_PROCESS
from pyoslc.vocabularies.jfs import JFS
from pyoslc.vocabularies.trs import OSLC_TRS

RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")


class JazzRootServiceSerializer(PrettyXMLSerializer):

    def __init__(self, store, max_depth=3):
        super(JazzRootServiceSerializer, self).__init__(store, max_depth=3)
        self.__root_serialized = {}
        self.__serialized = {}

    def serialize(self, stream, base=None, encoding=None, **args):
        self.__serialized = {}
        store = self.store

        # if base is given here, use that, if not and a base is set for the graph use that
        if base is not None:
            self.base = base
        elif store.base is not None:
            self.base = store.base

        self.max_depth = args.get("max_depth", 3)
        assert self.max_depth > 0, "max_depth must be greater than 0"

        self.nm = nm = store.namespace_manager
        self.writer = writer = XMLWriter(stream, nm, encoding)
        namespaces = {}

        possible = set(store.predicates()).union(store.objects(None, RDF.type))

        for predicate in possible:
            prefix, namespace, local = nm.compute_qname_strict(predicate)
            namespaces[prefix] = namespace

        namespaces["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        namespaces["dc"] = "http://purl.org/dc/terms/"
        namespaces["jd"] = JAZZ_DISCOVERY.uri
        namespaces["jfs"] = JFS.uri
        namespaces["trs"] = OSLC_TRS.uri
        namespaces["jp06"] = "http://jazz.net/xmlns/prod/jazz/process/0.6/"
        namespaces["jp"] = JAZZ_PROCESS.uri

        writer.push(RDF.Description)
        for subject in store.subjects():
            if not (None, None, subject) in store:
                writer.attribute(RDF.about, self.relativize(subject))
                self.__root_serialized[subject] = 1
                break

        if "xml_base" in args:
            writer.attribute(XMLBASE, args["xml_base"])
        elif self.base:
            writer.attribute(XMLBASE, self.base)

        writer.namespaces(list(namespaces.items()))

        # Write out subjects that can not be inline
        for subject in store.subjects():
            if (None, None, subject) in store:
                if (subject, None, subject) in store:
                    self.subject(subject, 1)
            else:
                self.subject(subject, 1)

        # write out anything that has not yet been reached
        # write out BNodes last (to ensure they can be inlined where possible)
        bnodes = set()

        for subject in store.subjects():
            if isinstance(subject, BNode):
                bnodes.add(subject)
                continue
            self.subject(subject, 1)

        # now serialize only those BNodes that have not been serialized yet
        for bnode in bnodes:
            if bnode not in self.__serialized:
                self.subject(subject, 1)

        writer.pop(RDF.Description)
        stream.write(b("\n"))

        # Set to None so that the memory can get garbage collected.
        self.__serialized = None
        self.__root_serialized = None

    def subject(self, subject, depth=1):
        store = self.store
        writer = self.writer

        if subject not in self.__serialized:
            self.__serialized[subject] = 1
            type = first(store.objects(subject, RDF.type))

            try:
                self.nm.qname(type)
            except TypeError:
                type = None

            element = type or RDF.Description

            if subject not in self.__root_serialized:
                writer.push(element)

            if isinstance(subject, BNode):
                def subj_as_obj_more_than(ceil):
                    return True
                    # more_than(store.triples((None, None, subject)), ceil)

                # here we only include BNode labels if they are referenced
                # more than once (this reduces the use of redundant BNode
                # identifiers)
                if subj_as_obj_more_than(1):
                    writer.attribute(RDF.nodeID, fix(subject))

            else:
                if subject not in self.__root_serialized:
                    writer.attribute(RDF.about, self.relativize(subject))

            if (subject, None, None) in store:
                for predicate, object in store.predicate_objects(subject):
                    if not (predicate == RDF.type and object == type):
                        self.predicate(predicate, object, depth + 1)

            if subject not in self.__root_serialized:
                writer.pop(element)

    def predicate(self, predicate, object, depth=1):
        writer = self.writer
        store = self.store
        writer.push(predicate)

        if isinstance(object, Literal):
            if object.language:
                writer.attribute(XMLLANG, object.language)

            if object.datatype == RDF.XMLLiteral and isinstance(object.value, xml.dom.minidom.Document):
                writer.attribute(RDF.parseType, "Literal")
                writer.text(u"")
                writer.stream.write(object)
            else:
                if object.datatype:
                    writer.attribute(RDF.datatype, object.datatype)
                writer.text(object)

        elif object in self.__serialized or not (object, None, None) in store:

            if isinstance(object, BNode):
                if more_than(store.triples((None, None, object)), 0):
                    writer.attribute(RDF.nodeID, fix(object))
            else:
                writer.attribute(RDF.resource, self.relativize(object))

        else:
            if first(store.objects(object, RDF.first)):  # may not have type RDF.List
                self.__serialized[object] = 1

                # Warn that any assertions on object other than
                # RDF.first and RDF.rest are ignored... including RDF.List
                import warnings

                warnings.warn("Assertions on %s other than RDF.first " % repr(
                    object) + "and RDF.rest are ignored ... including RDF.List",
                              UserWarning, stacklevel=2)
                writer.attribute(RDF.parseType, "Collection")

                col = Collection(store, object)

                for item in col:

                    if isinstance(item, URIRef):
                        self.forceRDFAbout.add(item)
                    self.subject(item)

                    if not isinstance(item, URIRef):
                        self.__serialized[item] = 1
            else:
                if first(store.triples_choices(
                    (object, RDF.type, [OWL_NS.Class, RDFS.Class]))) \
                        and isinstance(object, URIRef):
                    writer.attribute(RDF.resource, self.relativize(object))

                elif depth <= self.max_depth:
                    self.subject(object, depth + 1)

                elif isinstance(object, BNode):

                    if object not in self.__serialized and (object, None, None) in store and len(
                            list(store.subjects(object=object))) == 1:
                        # inline blank nodes if they haven't been serialized yet
                        # and are only referenced once (regardless of depth)
                        self.subject(object, depth + 1)
                    else:
                        writer.attribute(RDF.nodeID, fix(object))

                else:
                    writer.attribute(RDF.resource, self.relativize(object))

        writer.pop(predicate)
