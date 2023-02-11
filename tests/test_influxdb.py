from piholeinflux import Daemon


def test_send_msg(mocker, daemon_settings):
    """Test send_msg function, sending data to influxDB."""
    data = {"some": "value", "gravity_last_updated": "is not modified"}
    expected = {"measurement": "pihole", "tags": {"host": "myname"}, "fields": data}
    mock_write = mocker.patch("piholeinflux.write_api.WriteApi.write")
    d = Daemon(settings=daemon_settings)
    d.send_msg(data, "myname")

    mock_write.assert_called_with(bucket="pihole", record=expected)
    assert mock_write.call_count == 1
