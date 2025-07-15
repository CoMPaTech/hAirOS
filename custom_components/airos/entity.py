"""Generic AirOS Entity Class."""
from __future__ import annotations

from typing import Any

from homeassistant.const import CONF_HOST
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AirOSData, AirOSDataUpdateCoordinator


class AirOSEntity(CoordinatorEntity[AirOSData]):  # type:ignore [misc]
    """Represent a AirOS Entity."""

    coordinator: AirOSDataUpdateCoordinator

    def __init__(
        self,
        coordinator: AirOSDataUpdateCoordinator,
    ) -> None:
        """Initialise the gateway."""
        super().__init__(coordinator)

        data = coordinator.data.device_data
        host_data=data.get("host")

        configuration_url: str | None = None
        if entry := self.coordinator.config_entry:
            configuration_url = f"https://{entry.data[CONF_HOST]}"

        self._attr_device_info = DeviceInfo(
            configuration_url=configuration_url,
            identifiers={(DOMAIN, str(coordinator.data.device_id))},
            manufacturer="Ubiquiti",
            model=host_data.get("devmodel"),
            name=host_data.get("hostname"),
            sw_version=host_data.get("fwversion"),
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return super().available  # type: ignore[no-any-return]

    @property
    def device(self) -> dict[str, Any]:
        """Return data for this device."""
        return self.coordinator.data.device_id  # type: ignore[no-any-return]

    async def async_added_to_hass(self) -> None:
        """Subscribe to updates."""
        self._handle_coordinator_update()
        await super().async_added_to_hass()
