from piholeinflux import Pihole


def test_pihole_init():
    config = {"api_location": "http://here.example"}

    pihole = Pihole(config)

    assert hasattr(pihole, "name")
    assert hasattr(pihole, "url")
    assert hasattr(pihole, "timeout")

    assert pihole.name == "here.example"
    assert pihole.url == "http://here.example"
    assert pihole.timeout == 10
