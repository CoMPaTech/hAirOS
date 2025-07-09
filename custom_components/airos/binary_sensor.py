"""AirOS binary sensor component for Home Assistant."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AirOSDataUpdateCoordinator
from .entity import AirOSEntity


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
        value_fn=lambda data: data.get("services",{}).get("dhcpc"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="services_dhcp_server",
        translation_key="dhcp_server",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("services",{}).get("dhcpd"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="services_dhcp6_server",
        translation_key="dhcp6_server",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("services",{}).get("dhcp6d_stateful"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="services_pppoe",
        translation_key="pppoe",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("services",{}).get("pppoe"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="firewall_iptables",
        translation_key="firewall_iptables",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("firewall",{}).get("iptables"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="firewall_ebtables",
        translation_key="firewall_ebtables",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("firewall",{}).get("ebtables"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="firewall_ip6tables",
        translation_key="firewall_ip6tables",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("firewall",{}).get("ip6tables"),
        entity_registry_enabled_default=False,
    ),
    AirOSBinarySensorEntityDescription(
        key="firewall_eb6tables",
        translation_key="firewall_eb6tables",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("firewall",{}).get("eb6tables"),
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the AirOS sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    for description in BINARY_SENSORS:
        entities.append(AirOSBinarySensor(coordinator, description))

    async_add_entities(entities, update_before_add=False)


class AirOSBinarySensor(AirOSEntity, BinarySensorEntity):  # type: ignore[misc]
    """Representation of a Binary Sensor."""

    _attr_has_entity_name = True

    entity_description = AirOSBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: AirOSDataUpdateCoordinator,
        description: BinarySensorEntityDescription,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator

        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.device_id}_{description.key}"


    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator.data.device_data)


