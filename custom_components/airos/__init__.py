"""Ubiquiti AirOS platform for Home Assistant Core."""

from airos.airos8 import AirOS8

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, LOGGER, SCAN_INTERVAL
from .coordinator import AirOSDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AirOS from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    LOGGER.debug(f"AirOS entry: {entry}")

    # Fetch configuration data from config_flow
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    host = entry.data[CONF_HOST]

    airdevice = None

    try:
        LOGGER.debug("Attempting to instantiate AirOS8 client.")
        airdevice = AirOS8(host, username, password)

        device_data = await airdevice.interact_with_ubiquiti_device()
        LOGGER.debug("Interaction with Ubiquiti device successful.")

    except Exception as ex:
        # This will now catch errors from both AirOS8.__init__ and interact_with_ubiquiti_device()
        # The 'exc_info=True' is crucial for getting the full traceback.
        LOGGER.exception("Error during AirOS8 initialization or communication for %s.", host)
        raise ConfigEntryNotReady("Error while communicating to AirOS API") from ex

    host_data = device_data.get("host",{})
    interfaces_data = device_data.get("interfaces", [])
    device_id = host_data.get("device_id", host_data.get("hostname", host))
    hostname = host_data.get("hostname", host)
    devmodel = host_data.get("devmodel", "Unknown")

    mac_address: str | None = None
    # Iterate through interfaces to find eth0 and its MAC address
    for interface in interfaces_data:
       if interface.get("ifname") == "eth0":
          mac_address = interface.get("hwaddr")
          if mac_address:
              break


    if "device_id" not in entry.data:
        new_data = {
            **entry.data,
            "device_id": device_id,
            "hostname": hostname,
            "devmodel": devmodel,
        }
        hass.config_entries.async_update_entry(entry, data=new_data)

    # Use Device ID as unique id
    if entry.unique_id is None:
        hass.config_entries.async_update_entry(entry, unique_id=f"airos-{device_id}")

    # Set up coordinator for fetching data
    coordinator = AirOSDataUpdateCoordinator(hass, airdevice, SCAN_INTERVAL)  # type: ignore[arg-type]
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator for use in platforms
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Add device to the HA device registry
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        name=hostname,
        identifiers={(DOMAIN, str(device_id))},
        connections={(dr.CONNECTION_NETWORK_MAC, mac_address)},
        manufacturer="Ubiquity",
        sw_version=host_data.get("fwversion", "Unknown"),
        model=devmodel,
    )

    # Remove non-existing via device
    device_registry.async_update_device(
        device.id,
        name=hostname,
        model=devmodel,
        via_device_id=None,
    )

    # Set up platforms (i.e. sensors, binary_sensors)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok  # type: ignore [no-any-return]
