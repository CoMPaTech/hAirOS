"""Config flow for AirOS integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .airos8 import AirOS8
from .const import DOMAIN, LOGGER

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME, default="ubnt"): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_HOST): str,
    }
)


async def validate_input(_: HomeAssistant, data: dict[str, Any]) -> dict:
    """Validate the user input."""
    username = data[CONF_USERNAME]
    password = data[CONF_PASSWORD]
    base_url = data[CONF_HOST]

    airdevice = None

    try:
        LOGGER.debug("validate_input: Attempting to instantiate AirOS8 client with base_url='%s'...", base_url)
        airdevice = AirOS8(base_url, username, password)
        LOGGER.debug("validate_input: AirOS8 client instantiated successfully.")
    except Exception as e:
        # This block will catch *any* exception raised by AirOS8.__init__
        # The 'exc_info=True' will print the full traceback to your Home Assistant logs.
        LOGGER.exception("validate_input: Failed to instantiate AirOS8 client. Review traceback below for details.")
        # Re-raise as a Home Assistant specific exception
        raise CannotConnect from e # Assuming an instantiation error is a connection issue


    # If we reached here, airdevice should be defined.
    if airdevice is None: # Double-check, should not happen with the try-except
        LOGGER.error("validate_input: airdevice is unexpectedly None after instantiation attempt.")
        raise InvalidAuth # Fallback error

    LOGGER.error("validate_input: Attempting to interact with Ubiquiti device...")
    device_data = await airdevice.interact_with_ubiquiti_device()

    if not device_data:
        LOGGER.error("validate_input: No device data returned from interact_with_ubiquiti_device.")
        raise InvalidAuth

    LOGGER.error("validate_input: Credentials validated successfully. Returned device data: %s", device_data)

    return device_data


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg, misc]
    """Handle a config flow for AirOS."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            device_data = await validate_input(self.hass, user_input)
            LOGGER.error(f"device data contains {device_data}")

            host_data = device_data.get("host")
            device_id = host_data.get("device_id")
            hostname = host_data.get("hostname")

            await self.async_set_unique_id(f"airos-{device_id}")
            self._abort_if_unique_id_configured()

            LOGGER.info(f"Creating entry using {hostname} as AirOS device name")
            return self.async_create_entry(title=hostname, data=user_input)

        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):  # type: ignore[misc]
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):  # type: ignore[misc]
    """Error to indicate there is invalid auth."""
