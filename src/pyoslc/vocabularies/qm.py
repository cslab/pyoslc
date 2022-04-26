from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

OSLC_QM = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/qm#"),
    terms=[
        # RDFS Classes in this namespace
        "TestPlan",
        "TestCase",
        "TestScript",
        "TestExecutionRecord",
        "TestResult",
        # RDF Properties in this namespace
        "affectedByChangeRequest",
        "blockedByChangeRequest",
        "executesTestScript",
        "executionInstructions",
        "producedByTestExecutionRecord",
        "relatedChangeRequest",
        "reportsOnTestCase",
        "reportsOnTestPlan",
        "runsOnTestEnvironment",
        "runsTestCase",
        "status",
        "testsChangeRequest",
        "usesTestCase",
        "usesTestScript",
        "validatesRequirement",
        "validatesRequirementCollection",
    ],
)
