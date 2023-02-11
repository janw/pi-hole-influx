import pytest

from piholeinflux import Pihole

PAYLOAD_FIXTURE = {
    "domains_being_blocked": 86424,
    "dns_queries_today": 222897,
    "ads_blocked_today": 1716,
    "ads_percentage_today": 0,
    "unique_domains": 2326,
    "queries_forwarded": 20657,
    "queries_cached": 200516,
    "clients_ever_seen": 24,
    "unique_clients": 24,
    "dns_queries_all_types": 222897,
    "reply_NODATA": 181,
    "reply_NXDOMAIN": 6,
    "reply_CNAME": 49,
    "reply_IP": 784,
    "privacy_level": 0,
    "status": "enabled",
    "gravity_last_updated": {
        "file_exists": True,
        "absolute": 1589269042,
        "relative": {"days": 0, "hours": 0, "minutes": 6},
    },
}


def test_pihole_init(daemon_settings):
    """Test object initialization."""
    config = {"name": "pihole", "url": "http://here.example"}

    pihole = Pihole(settings=daemon_settings, **config)

    assert hasattr(pihole, "name")
    assert hasattr(pihole, "url")
    assert hasattr(pihole, "request_timeout")

    assert pihole.name == "pihole"
    assert pihole.url == "http://here.example"
    assert pihole.request_timeout == 10
    assert pihole.request_verify_ssl is True


@pytest.mark.vcr()
def test_pihole_get_data(daemon_settings):
    """Test getting data from an API endpoint."""
    config = {"name": "pihole1", "url": "http://127.0.0.1:8080/admin/api.php"}

    pihole = Pihole(settings=daemon_settings, **config)

    response = pihole.get_data()
    assert "domains_being_blocked" in response
    assert "ads_percentage_today" in response
    assert "gravity_last_updated" in response


def test_data_sanitizer():
    """Test proper sanitizing of data."""

    def IsOfType(cls):
        class IsOfType(cls):
            def __eq__(self, other):
                return isinstance(other, cls)

        return IsOfType()

    data = Pihole.sanitize_payload(PAYLOAD_FIXTURE)

    assert data is not PAYLOAD_FIXTURE
    assert "domains_being_blocked" in data
    assert "ads_percentage_today" in data
    assert "gravity_last_updated" in data
    assert isinstance(data["ads_percentage_today"], float)
    assert isinstance(data["gravity_last_updated"], int)


def test_data_sanitizer_last_updated_dict():
    payload = {"gravity_last_updated": "we don't want this"}
    data = Pihole.sanitize_payload(payload)

    assert len(data) == 0
