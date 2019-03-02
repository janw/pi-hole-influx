import io
from os import path

import pytest
from piholeinflux import main

CONFIG_FILE_CONTENT = """
[defaults]

request_timeout = 10
reporting_interval = 30

[influxdb]
port = 8086
hostname = 10.10.10.1
username = pihole
password = allthosesweetumstatistics
database = pihole

[pihole]
api_location = http://127.0.0.1:8080/admin/api.php
"""

CONFIG_FILE_CONTENT_INSTANCE_NAME = (
    CONFIG_FILE_CONTENT + "instance_name = testinstance\n"
)
HERE = path.dirname(path.dirname(path.realpath(__file__)))


@pytest.mark.vcr()
def test_main(mocker):
    """Test main function executed when running the daemon."""
    mock_config = mocker.patch(
        "builtins.open", return_value=io.StringIO(CONFIG_FILE_CONTENT)
    )

    with mock_config:
        main(single_run=True)

    mock_config.assert_called_with(path.join(HERE, "config.ini"))


@pytest.mark.vcr()
def test_main_instance_name(mocker):
    """Test main function executed, configured with instanec_name."""
    mock_config = mocker.patch(
        "builtins.open", return_value=io.StringIO(CONFIG_FILE_CONTENT_INSTANCE_NAME)
    )

    with mock_config:
        main(single_run=True)

    mock_config.assert_called_with(path.join(HERE, "config.ini"))


@pytest.mark.vcr()
def test_main_exception(mocker):
    """Test main function, failing with exceptino inside of loop."""
    mock_config = mocker.patch(
        "builtins.open", return_value=io.StringIO(CONFIG_FILE_CONTENT)
    )
    mock_get_data = mocker.patch(
        "piholeinflux.Pihole.get_data", side_effect=ConnectionError
    )

    with mock_config:
        with pytest.raises(SystemExit) as ctx:
            main(single_run=True)

    assert ctx.value.code == 1
    mock_get_data.assert_called_once_with()
