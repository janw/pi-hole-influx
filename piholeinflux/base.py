import logging
import sys

from piholeinflux.daemon import Daemon
from piholeinflux.settings import settings

logger = logging.getLogger(__name__)


def main(single_run=False):
    log_level = (settings.LOG_LEVEL).upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(levelname)s: [%(name)s] %(message)s",
    )

    daemon = Daemon(single_run)

    try:
        daemon.run()
    except KeyboardInterrupt:
        sys.exit(0)  # pragma: no cover
    except Exception:
        logger.exception("Unexpected exception", exc_info=True)
        sys.exit(1)
