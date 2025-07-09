"""AirOS constants for Home Assistant."""

from datetime import timedelta
import logging

DOMAIN = "airos"
LOGGER = logging.getLogger(__name__)

COORDINATOR = "coordinator"

SCAN_INTERVAL = timedelta(minutes=1)

