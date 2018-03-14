import pytest

from lightbus.config import make_transport_selector_structure, make_api_config_structure
from lightbus.transports.debug import DebugEventTransport
from lightbus.transports.redis import RedisEventTransport

pytestmark = pytest.mark.unit


def test_make_transport_config_structure():
    EventTransportSelector = make_transport_selector_structure('event')
    assert 'redis' in EventTransportSelector.__annotations__


def test_make_api_config_structure():
    ApiConfig = make_api_config_structure()
    assert 'event_transport' in ApiConfig.__annotations__
    assert 'rpc_transport' in ApiConfig.__annotations__
    assert 'result_transport' in ApiConfig.__annotations__
    assert 'schema_transport' in ApiConfig.__annotations__
