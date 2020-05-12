from piholeinflux import Daemon


def test_send_msg(mocker):
    """Test send_msg function, sending data to influxDB."""
    data = {"some": "value", "gravity_last_updated": "is not modified"}
    expected = [{"measurement": "pihole", "tags": {"host": "myname"}, "fields": data}]
    mock_influx = mocker.patch("piholeinflux.InfluxDBClient")
    d = Daemon()
    d.send_msg(data, "myname")

    mock_influx().write_points.assert_called_with(expected)
    assert mock_influx().write_points.call_count == 1
