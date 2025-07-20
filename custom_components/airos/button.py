"""AirOS button component for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import AirOSDataUpdateCoordinator
from .entity import AirOSEntity
from .helpers import get_client_device_info, get_client_mac

_LOGGER = logging.getLogger(__name__)

BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="restart",
    device_class=ButtonDeviceClass.RESTART,
    translation_key="restart_connection"
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the AirOS button from a config entry."""
    coordinator = config_entry.runtime_data
    entities: list[AirOSClientButton] = []

    wireless_data = coordinator.data.device_data.get("wireless", {})

    if "sta" in wireless_data:
        for client_data in wireless_data["sta"]:
            entities.extend(AirOSClientButton(coordinator, client_data))

    async_add_entities(entities, update_before_add=False)


class AirOSClientButton(AirOSEntity, ButtonEntity):
    """Represents a button to force restart connection for a client."""

    _attr_has_entity_name = True
    _attr_device_class = ButtonDeviceClass.RESTART

    entity_description: ButtonEntityDescription

    def __init__(self, coordinator: AirOSDataUpdateCoordinator, client_data: dict) -> None:
        """Initialize the AirOS client button."""
        super().__init__(coordinator)
        self._client_data = client_data
        self.coordinator = coordinator
        self.entity_description = BUTTON_DESCRIPTION

        self.mac_lower = get_client_mac(self._client_data)
        self._attr_unique_id = f"{coordinator.config_entry.unique_id}_{self.mac_lower}_restart_connection"

        self._attr_device_info = get_client_device_info(coordinator.config_entry.unique_id, self._client_data)

        self._attr_name = "Restart Connection"

    async def async_press(self) -> None:
        """Handle the button press to force restart the client connection."""
        mac_address = self._client_data.get("mac")
        if not mac_address:
            _LOGGER.error("Cannot restart connection: MAC address not found for client")
            return

        log = f"Attempting to force restart connection for client: {mac_address}"
        _LOGGER.error(log)
        try:
            await self.coordinator.airdevice.login()
            result = await self.coordinator.airdevice.stakick(mac_address)
            log = f"Restart resulted in {result}"
            _LOGGER.error(log)

        except Exception as e:  # noqa: BLE001
            log = f"Failed to restart client {mac_address}: {e}"
            _LOGGER.error(log)

    def _get_remote_type(self) -> str:
        """Determine remote type."""
        return "Access Point/Uplink" if self._client_data.get("remote",{}).get("mode","") == "ap-ptp" else "Station"
