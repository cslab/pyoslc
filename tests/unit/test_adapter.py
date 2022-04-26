from pyoslc.vocabularies.qm import OSLC_QM
from pyoslc.vocabularies.rm import OSLC_RM


def test_base_adapter(base_adapter):

    assert (
        base_adapter.identifier and base_adapter.identifier != ""
    ), "Identifier should be initialized"
    assert (
        base_adapter.title and base_adapter.title != ""
    ), "Title should be initialized"
    assert not base_adapter.domain, "Domain should be empty for base adapter"
    assert not base_adapter.types, "Types should be empty for base adapter"


def test_rm_adapter(rm_adapter):
    assert (
        rm_adapter.identifier and rm_adapter.identifier == "rmtest"
    ), "Identifier should be initialized"
    assert (
        rm_adapter.title and rm_adapter.title == "RM Test"
    ), "Title should be initialized"
    assert rm_adapter.domain == OSLC_RM, "The domain attribute should be RM"
    assert rm_adapter.types == [OSLC_RM.Requirement]


def test_tc_adapter(tc_adapter):
    assert (
        tc_adapter.identifier and tc_adapter.identifier == "tctest"
    ), "Identifier should be initialized"
    assert (
        tc_adapter.title and tc_adapter.title == "QM Test"
    ), "Title should be initialized"
    assert tc_adapter.domain == OSLC_QM, "The domain attribute should be QM"
    assert tc_adapter.types == [OSLC_QM.TestCase]
