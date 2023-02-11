#! /usr/bin/env python3
from __future__ import annotations

import logging
import sys
from os import environ
from pathlib import Path
from time import sleep
from typing import Literal, Optional, Union

import requests
import tomli
from influxdb_client import InfluxDBClient
from influxdb_client.client import write_api
from pydantic import AnyHttpUrl, BaseSettings, validator

logger = logging.getLogger("piholeinflux")


class InstanceSettings(BaseSettings):
    name: str = "pihole"
    base_url: AnyHttpUrl = "http://127.0.0.1"
    api_token: str = ""

    @validator("base_url")
    def base_url_must_not_contain_api_path(cls, value: AnyHttpUrl) -> AnyHttpUrl:
        path = value.path
        if path and "admin/api.php" in path:
            raise ValueError("Must not contain the API path of the Pi-hole instance")
        return value

    def get_full_url(self) -> str:
        url = self.base_url
        url.path = (url.path.rstrip("/") if url.path else "") + "/admin/api.php"
        url.query = "summaryRaw"

        return AnyHttpUrl.build(
            scheme=url.scheme,
            user=url.user,
            password=url.password,
            host=url.host,
            port=url.port,
            path=url.path,
            query=url.query,
            fragment=url.fragment,
        )


class Settings(BaseSettings):
    log_level: Literal["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"] = "INFO"

    influxdb_url: AnyHttpUrl = "http://127.0.0.1:8086"
    influxdb_token: str
    influxdb_org: str
    influxdb_bucket: str = "pihole"
    influxdb_verify_ssl: bool = True

    request_timeout: int = 10
    request_verify_ssl: bool = True
    reporting_interval: int = 30

    instances: list[InstanceSettings] = [InstanceSettings()]

    class Config:
        env_prefix = "pihole_"

    @validator("log_level", pre=True)
    def log_level_uppercase(cls, value: str) -> str:
        return value.upper()

    @classmethod
    def from_toml(cls, path: Path) -> Settings:
        return cls.parse_obj(tomli.loads(path.read_text()))

    @classmethod
    def load_user_conf(cls) -> Settings:
        user_conf = Path(environ.get("PIHOLE_CONFIG_FILE", "user.toml"))
        return cls.from_toml(user_conf)


class Pihole:
    """Container object for a single Pi-hole instance."""

    def __init__(
        self,
        name: str,
        url: str,
        settings: Settings,
        auth: Union[str, None] = None,
    ) -> None:
        self.name = name
        self.url = url
        self.request_timeout = settings.request_timeout
        self.request_verify_ssl = settings.request_verify_ssl

        self.logger = logging.getLogger("pihole." + name)
        self.logger.info(
            "Initialized for Pi-hole instance '%s' (endpoint: %s)", name, url
        )

        if not self.request_verify_ssl:
            self.logger.warning("Disabled SSL verification for Pi-hole requests")

        self.request_params = {}
        if auth:
            self.request_params["auth"] = auth

    @classmethod
    def from_settings(
        cls, instance_settings: InstanceSettings, global_settings: Settings
    ) -> Pihole:
        return cls(
            name=instance_settings.name,
            url=instance_settings.get_full_url(),
            settings=global_settings,
            auth=instance_settings.api_token,
        )

    def get_data(self) -> Union[dict, None]:
        """Retrieve API data from Pi-hole, and return as dict on success."""
        self.logger.debug("Querying %s", self.url)
        response = requests.get(
            self.url,
            timeout=self.request_timeout,
            verify=self.request_verify_ssl,
            params=self.request_params,
        )
        if response.status_code == 200:
            self.logger.debug("Got response:\n    %s", response.content)
            return self.check_and_sanitize_payload(response.json())
        else:
            self.logger.error(
                "Got unexpected response %d, %s", response.status_code, response.content
            )

    def check_and_sanitize_payload(self, data: dict) -> Union[dict, None]:
        if isinstance(data, list) and len(data) == 0:
            self.logger.error(
                "Received empty payload, indicating wrong API token: '%s'", data
            )
            return
        if not data or not isinstance(data, dict):
            self.logger.error("Received unexpected payload: '%s'", data)
            return

        data = data.copy()
        if "gravity_last_updated" in data:
            if "absolute" in data["gravity_last_updated"]:
                data["gravity_last_updated"] = data["gravity_last_updated"]["absolute"]
            else:
                del data["gravity_last_updated"]

        # Monkey-patch ads-% to be always float (type not enforced at API level)
        if "ads_percentage_today" in data:
            data["ads_percentage_today"] = float(data["ads_percentage_today"])

        return data


class Daemon:
    def __init__(self, settings: Settings, single_run: bool = False) -> None:
        logger.info(
            "Launching daemon to report to InfluxDB '%s'", settings.influxdb_url
        )
        influx = InfluxDBClient(
            url=settings.influxdb_url,
            org=settings.influxdb_org,
            token=settings.influxdb_token,
            verify_ssl=settings.influxdb_verify_ssl,
        )
        write_options = write_api.WriteOptions(
            batch_size=len(settings.instances) * 2,
            flush_interval=60_000,  # milliseconds
        )
        self.influx_api = influx.write_api(write_options=write_options)
        self.influx_bucket = settings.influxdb_bucket
        self.single_run = single_run
        self.piholes = [
            Pihole.from_settings(instance_settings=inst, global_settings=settings)
            for inst in settings.instances
        ]
        self.reporting_interval = settings.reporting_interval

    def run(self) -> None:
        while True:
            for pi in self.piholes:
                if not (data := pi.get_data()):
                    continue
                self.send_msg(data, pi.name)

            if self.single_run:
                logger.info("Finished single run.")
                break
            sleep(self.reporting_interval)  # pragma: no cover

    def send_msg(self, resp: dict, name: str) -> None:
        record = {
            "measurement": "pihole",
            "tags": {
                "host": name,
            },
            "fields": resp,
        }
        self.influx_api.write(bucket=self.influx_bucket, record=record)

    def shutdown(self) -> None:
        logger.info("Shutting down")
        self.influx_api.close()


def main(settings: Optional[Settings] = None, single_run: bool = False) -> None:
    if not settings:
        settings = Settings.load_user_conf()

    log_level = settings.log_level
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(levelname)s: [%(name)s] %(message)s",
    )

    daemon = Daemon(settings=settings, single_run=single_run)

    try:
        daemon.run()
    except KeyboardInterrupt:  # pragma: no cover
        daemon.shutdown()
        sys.exit(0)
    except Exception:
        logger.exception("Unexpected exception", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
