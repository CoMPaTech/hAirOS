"""Helpers for airOS."""
from __future__ import annotations

import logging
from typing import Any

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

def get_client_device_info(coordinator_unique_id: str, client_data: dict) -> dict[str, Any]:
    """Generate device info for a client."""
    remote_type = "Access Point/Uplink" if client_data.remote.mode == "ap-ptp" else "Station"
    hostname = client_data.remote.hostname

    mac_lower = client_data.mac.lower()

    return {
        "identifiers": {(DOMAIN, f"remote_{mac_lower}")},
        "name": f"Remote {remote_type}: {hostname}",
        "via_device": (DOMAIN, coordinator_unique_id),
    }
