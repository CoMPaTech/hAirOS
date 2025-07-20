"""AirOS binary sensor component for Home Assistant."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import AirOSDataUpdateCoordinator
from .entity import AirOSEntity
from .helpers import get_client_device_info, get_client_mac

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class AirOSBinarySensorEntityDescription(BinarySensorEntityDescription):  # type: ignore[misc]
    """Describe an AirOS binary_sensor."""

    value_fn: Callable[[dict[str, Any]], bool | None]


BINARY_SENSORS: tuple[AirOSBinarySensorEntityDescription, ...] = (
    AirOSBinarySensorEntityDescription(
        key="portfw",
        translation_key="port_forwarding",
        device_class=BinarySensorDeviceClass.DOOR,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("portfw"),
    ),
    AirOSBinarySensorEntityDescription(
        key="services_dhcp_client",
        translation_key="dhcp_client",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("services", {}).get("dhcpc"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="services_dhcp_server",
        translation_key="dhcp_server",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("services", {}).get("dhcpd"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="services_dhcp6_server",
        translation_key="dhcp6_server",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("services", {}).get("dhcp6d_stateful"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="services_pppoe",
        translation_key="pppoe",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("services", {}).get("pppoe"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="firewall_iptables",
        translation_key="firewall_iptables",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("firewall", {}).get("iptables"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="firewall_ebtables",
        translation_key="firewall_ebtables",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("firewall", {}).get("ebtables"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="firewall_ip6tables",
        translation_key="firewall_ip6tables",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("firewall", {}).get("ip6tables"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="firewall_eb6tables",
        translation_key="firewall_eb6tables",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("firewall", {}).get("eb6tables"),
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
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the AirOS sensors from a config entry."""
    coordinator = config_entry.runtime_data

    entities = [
        AirOSBinarySensor(coordinator, description) for description in BINARY_SENSORS
    ]

    wireless_data = coordinator.data.device_data.get("wireless", {})

    # Determine remote stations
    if "sta" in wireless_data:
        for client_data in wireless_data["sta"]:
            entities.append(AirOSClientBinarySensor(coordinator, client_data, wireless_data["sta"]))

    async_add_entities(entities, update_before_add=False)


class AirOSBinarySensor(AirOSEntity, BinarySensorEntity):  # type: ignore[misc]
    """Representation of a Binary Sensor."""

    _attr_has_entity_name = True

    entity_description = AirOSBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: AirOSDataUpdateCoordinator,
        description: BinarySensorEntityDescription,
    ):  # pylint: disable=hass-return-type
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator

        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.device_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator.data.device_data)


class AirOSClientBinarySensor(AirOSEntity, BinarySensorEntity):
    """Represents a connected client (station) to the AirOS device."""

    _attr_has_entity_name = True

    entity_description: BinarySensorEntityDescription
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: AirOSDataUpdateCoordinator, client_data: str, clients: dict) -> None:
        """Initialize the AirOS client binary sensor."""
        super().__init__(coordinator)
        self._client_data = client_data
        self._clients = clients
        self.coordinator = coordinator
        self.entity_description = CLIENT_BINARY_SENSOR_DESCRIPTION

        mac_lower = get_client_mac(self._client_data)
        self._attr_unique_id = f"{coordinator.config_entry.unique_id}_{mac_lower}_connectivity"

        self._attr_device_info = get_client_device_info(coordinator.config_entry.unique_id, self._client_data)

        self._update_client_attributes()


    @property
    def is_on(self) -> bool | None:
        """Return true if the client is currently connected."""
        for client in self._clients:
            if client.get("mac") == self._client_data.get("mac"):
                return True # Client found, thus connected
            return False # Client not found in the current list, thus disconnected
        return None # Return None if not in AP mode or no client data

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_client_attributes() # Update name if hostname changes
        super()._handle_coordinator_update()

    def _update_client_attributes(self) -> None:
        """Update entity attributes based on current data."""
        if self._client_data and "hostname" in self._client_data.get("remote",{}):
            self._attr_name = self._client_data.get("remote",{})["hostname"]
