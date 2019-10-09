import logging

import requests

from piholeinflux.settings import settings

logger = logging.getLogger(__name__)


class Pihole:
    """Container object for a single Pi-hole instance."""

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.timeout = settings.as_int("REQUEST_TIMEOUT")
        self.logger = logging.getLogger("pihole." + name)
        self.logger.info("Initialized for %s (%s)", name, url)

    def get_data(self):
        """Retrieve API data from Pi-hole, and return as dict on success."""
        response = requests.get(self.url, timeout=self.timeout)
        if response.status_code == 200:
            self.logger.debug("Got %d bytes", len(response.content))
            return response.json()
        else:
            self.logger.error(
                "Got unexpected response %d, %s", response.status_code, response.content
            )
