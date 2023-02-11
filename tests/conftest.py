import pytest

from piholeinflux import InstanceSettings, Settings


@pytest.fixture
def daemon_settings():
    return Settings(
        influxdb_token="dummtoken",
        influxdb_org="dummyorg",
        request_timeout=10,
        request_verify_ssl=True,
        reporting_interval=30,
        instances=[
            InstanceSettings(
                name="localhost",
                base_url="http://127.0.0.1:8080",
            )
        ],
    )
