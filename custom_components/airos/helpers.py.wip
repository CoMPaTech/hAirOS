"""Helpers for airOS."""
from __future__ import annotations

import logging

from airos.data import Station

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .coordinator import AirOSDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

def get_client_device_info(coordinator: AirOSDataUpdateCoordinator, client_data: Station) -> DeviceInfo:
    """Generate device info for a client."""
    remote_type = "Access Point/Uplink" if client_data.remote.mode.value == "ap-ptp" else "Station"

    mac_lower = client_data.mac.lower()
    unique_id = coordinator.config_entry.unique_id

    device_info: DeviceInfo = {
        "identifiers": {(DOMAIN, f"remote_{mac_lower}")},
        "name": f"Remote {remote_type}: {client_data.remote.hostname}",
    }
    if unique_id:
        device_info["via_device"] = (DOMAIN, unique_id)
    return device_info
