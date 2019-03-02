import pytest
from piholeinflux import Pihole


def test_pihole_init():
    """Test object initialization."""
    config = {"api_location": "http://here.example"}

    pihole = Pihole(config)

    assert hasattr(pihole, "name")
    assert hasattr(pihole, "url")
    assert hasattr(pihole, "timeout")

    assert pihole.name == "here.example"
    assert pihole.url == "http://here.example"
    assert pihole.timeout == 10


@pytest.mark.vcr()
def test_pihole_get_data():
    """Test getting data from an API endpoint."""
    config = {"api_location": "http://127.0.0.1:8080/admin/api.php"}

    pihole = Pihole(config)

    response = pihole.get_data()
    assert "domains_being_blocked" in response
    assert "ads_percentage_today" in response
    assert "gravity_last_updated" in response
