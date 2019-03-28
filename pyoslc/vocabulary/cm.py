from rdflib import URIRef
from rdflib.namespace import ClosedNamespace

OSLC_CM = ClosedNamespace(
    uri=URIRef("http://open-services.net/ns/cm#"),
    terms=[
        # RDFS Classes in this namespace
        "ChangeNotice", "ChangeRequest", "Defect",
        "Enhancement", "Priority", "ReviewTask", "Severity",
        "State", "Task"

        # RDF Properties in this namespace
        "affectedByDefect", "affectsPlanItem",
        "affectsRequirement", "affectsTestResult",
        "authorizer", "blocksTestExecutionRecord",
        "closeDate", "implementsRequirement", "parent",
        "priority", "relatedChangeRequest", "relatedTestCase",
        "relatedTestExecutionRecord", "relatedTestPlan",
        "relatedTestScript", "severity", "state", "status",
        "testedByTestCase", "tracksChangeSet", "tracksRequirement"
    ]
)
