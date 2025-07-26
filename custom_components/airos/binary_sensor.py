"""AirOS Binary Sensor component for Home Assistant."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from airos.data import Station

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .coordinator import AirOSConfigEntry, AirOSData, AirOSDataUpdateCoordinator
from .entity import AirOSEntity
from .helpers import get_client_device_info

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class AirOSBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe an AirOS binary sensor."""

    value_fn: Callable[[AirOSData], StateType]


BINARY_SENSORS: tuple[AirOSBinarySensorEntityDescription, ...] = (
    AirOSBinarySensorEntityDescription(
        key="portfw",
        translation_key="port_forwarding",
        device_class=BinarySensorDeviceClass.DOOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.portfw,
    ),
    AirOSBinarySensorEntityDescription(
        key="dhcp_client",
        translation_key="dhcp_client",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.services.dhcpc,
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="dhcp_server",
        translation_key="dhcp_server",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.services.dhcpd,
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="dhcp6_server",
        translation_key="dhcp6_server",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.services.dhcp6d_stateful,
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="pppoe",
        translation_key="pppoe",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.services.pppoe,
        entity_registry_enabled_default=False,
    ),
)

CLIENT_BINARY_SENSOR_DESCRIPTION = BinarySensorEntityDescription(
    key="connectivity",
    device_class=BinarySensorDeviceClass.CONNECTIVITY,
    translation_key="client_connectivity"
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AirOSConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the AirOS binary sensors from a config entry."""
    coordinator = config_entry.runtime_data

    async_add_entities([AirOSBinarySensor(coordinator, description) for description in BINARY_SENSORS], update_before_add=False)

    # Determine remote stations
    stations = coordinator.data.wireless.sta
    async_add_entities([AirOSClientBinarySensor(coordinator, client_data, stations) for client_data in stations], update_before_add=False)


class AirOSBinarySensor(AirOSEntity, BinarySensorEntity):
    """Representation of a binary sensor."""

    entity_description: AirOSBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: AirOSDataUpdateCoordinator,
        description: AirOSBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.host.device_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return the state of the binary sensor."""
        return bool(self.entity_description.value_fn(self.coordinator.data))


class AirOSClientBinarySensor(AirOSEntity, BinarySensorEntity):
    """Represents a connected client (station) to the AirOS device."""

    entity_description: BinarySensorEntityDescription

    def __init__(self, coordinator: AirOSDataUpdateCoordinator, client_data: Station, clients: list[Station]) -> None:
        """Initialize the AirOS client binary sensor."""
        super().__init__(coordinator)
        self._client_data = client_data
        self._clients = clients

        mac_lower = self._client_data.mac.lower()
        self._attr_unique_id = f"{coordinator.config_entry.unique_id}_{mac_lower}_connectivity"

        self._attr_device_info = get_client_device_info(coordinator, self._client_data)

        self._update_client_attributes()


    @property
    def is_on(self) -> bool | None:
        """Return true if the client is currently connected."""
        for client in self._clients:
            if client.mac == self._client_data.mac:
                return True # Client found, thus connected
            return False # Client not found in the current list, thus disconnected
        return None # Return None if not in AP mode or no client data

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_client_attributes() # Update name if hostname changes
        super()._handle_coordinator_update()

    def _update_client_attributes(self) -> None:
        """Update entity attributes based on current data."""
        self._attr_name = self._client_data.remote.hostname
