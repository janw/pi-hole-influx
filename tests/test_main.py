from piholeinflux import main

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

"""


def test_main(mocker):
    indata = {"some": "value", "gravity_last_updated": "should be gone"}
    expected = [{
        "measurement": "pihole",
        "tags": {"host": "myname"},
        "fields": {"some": "value"},
    }]
    mock_influx = mocker.patch("influxdb.InfluxDBClient")
    mock_open = mocker.mock_open(read_data=CONFIG_FILE_CONTENT)

    main()

    mock_open.assert_called()
