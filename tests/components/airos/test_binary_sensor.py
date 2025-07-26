"""Test the Ubiquiti airOS binary sensors."""

from unittest.mock import AsyncMock

from homeassistant.components.airos.coordinator import AirOSData
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from syrupy.assertion import SnapshotAssertion

from . import setup_integration

from tests.common import MockConfigEntry

# Mock data for various scenarios
MOCK_CONFIG = {
    CONF_HOST: "1.1.1.1",
    CONF_USERNAME: "test_user",
    CONF_PASSWORD: "test_password",
}


async def test_all_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_airos_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
    ap_fixture: AirOSData,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test all entities."""
    await setup_integration(hass, mock_config_entry)

