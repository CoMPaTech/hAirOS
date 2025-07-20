"""Helpers for airOS."""
from __future__ import annotations

import logging
from typing import Any

from airos.exceptions import DataMissingError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

def get_client_mac(client_data: dict) -> str:
    """Determine client mac address."""
    try:
        return client_data["mac"].replace(":", "").lower()
    except KeyError as e:
        _LOGGER.error("MAC address missing in client data")
        raise DataMissingError from e

def get_client_device_info(coordinator_unique_id: str, client_data: dict) -> dict[str, Any]:
    """Generate device info for a client."""
    remote_type = "Access Point/Uplink" if client_data.get("remote",{}).get("mode","") == "ap-ptp" else "Station"
    hostname = client_data.get("remote",{}).get("hostname","Unknown")

    mac_lower = get_client_mac(client_data)

    return {
        "identifiers": {(DOMAIN, f"remote_{mac_lower}")},
        "name": f"Remote {remote_type}: {hostname}",
        "via_device": (DOMAIN, coordinator_unique_id),
    }
