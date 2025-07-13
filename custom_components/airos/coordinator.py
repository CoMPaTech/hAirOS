"""DataUpdateCoordinator for AirOS."""
from typing import Any, NamedTuple

from airos.airos8 import AirOS8

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, SCAN_INTERVAL


class AirOSData(NamedTuple):
    """AirOS data stored in the DataUpdateCoordinator."""

    device_data: dict[str, Any]
    device_id: str
    hostname: str


class AirOSDataUpdateCoordinator(DataUpdateCoordinator[AirOSData]):  # type: ignore[misc]
    """Class to manage fetching AirOS data from single endpoint."""

    def __init__(self, hass: HomeAssistant, airdevice: AirOS8, interval: float) -> None:
        """Initialize the coordinator."""
        super().__init__(hass, LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.airdevice = airdevice

    async def _async_update_data(self) -> AirOSData:
        """Fetch data from AirOS."""
        try:
            await self.airdevice.login()
            api_response = await self.airdevice.status()

            host_data = api_response.get("host")
            device_id = host_data.get("device_id")
            hostname = host_data.get("hostname")

            data = [api_response, device_id, hostname]
            LOGGER.error("AirOS data %s updated", data)

        except Exception as err:
            raise ConfigEntryAuthFailed from err
        return AirOSData(*data)  # type: ignore [arg-type]
