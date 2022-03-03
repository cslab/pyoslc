import logging
import pytest

from apposlc.adapter import RequirementAdapter, TestCaseAdapter
from tests.functional.oslc import PyOSLC

from apposlc import create_oslc_app

from tests.unit.adapter import RMAdapter, BaseAdapter


logging.basicConfig(level=logging.DEBUG)
logging.getLogger(__name__)


@pytest.fixture(scope='session')
def client_oslc():
    oslc_app = create_oslc_app()
    oslc_app.app.testing = True
    with oslc_app.app.test_client() as client:
        with oslc_app.app.app_context():
            yield client  # this is where the testing happens!


@pytest.fixture
def pyoslc(client_oslc):
    logger.debug("Initializing OSLC Client")
    return PyOSLC(client_oslc)


@pytest.fixture
def pyoslc_enabled(client_oslc):
    return PyOSLC(client_oslc)


@pytest.fixture
def base_adapter():
    return BaseAdapter()


@pytest.fixture
def rm_adapter():
    return RequirementAdapter(identifier='rmtest', title='RM Test', mapping=None)


@pytest.fixture
def tc_adapter():
    return TestCaseAdapter(identifier='tctest', title='QM Test', mapping=None)
