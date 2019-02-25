CONFIG_FILE_CONTENT = """
[defaults]

request_timeout = 10
reporting_interval = 30

[influxdb]
port = 8086
hostname = 10.10.4.9
username = pihole
password = allthosesweetstatistics
database = pihole

[pihole]
api_location = http://127.0.0.1:8080/admin/api.php
"""


def test_main(mocker):
    """Test main function executed when running the daemon."""
    pass
