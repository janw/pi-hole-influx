import pytest
from piholeinflux import main


@pytest.mark.vcr()
def test_main(mocker):
    """Test main function executed when running the daemon."""
    mock_influx = mocker.patch("piholeinflux.InfluxDBClient")

    main(single_run=True)

    assert mock_influx.called
    assert mock_influx.call_count == 1


@pytest.mark.vcr()
def test_main_exception(mocker):
    """Test main function, failing with exceptino inside of loop."""
    mock_influx = mocker.patch("piholeinflux.InfluxDBClient")
    mock_get_data = mocker.patch(
        "piholeinflux.Pihole.get_data", side_effect=ConnectionError
    )

    with pytest.raises(SystemExit) as ctx:
        main(single_run=True)

    assert ctx.value.code == 1
    mock_get_data.assert_called_with()
    assert mock_influx.called
    assert mock_influx.call_count == 1
