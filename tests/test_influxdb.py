from piholeinflux import send_msg


def test_send_msg(mocker):
    """Test send_msg function, sending data to influxDB."""
    indata = {"some": "value", "gravity_last_updated": "should be gone"}
    expected = [
        {
            "measurement": "pihole",
            "tags": {"host": "myname"},
            "fields": {"some": "value"},
        }
    ]
    mock_influx = mocker.patch("influxdb.InfluxDBClient")

    send_msg(mock_influx(), indata, "myname")

    mock_influx().write_points.assert_called_once_with(expected)
