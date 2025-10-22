"""Config flow for Energy Data Importer integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import CONF_INSTANCE_NAME, DATA_SOURCES, DOMAIN

_LOGGER = logging.getLogger(__name__)


class EnergyDataImporterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energy Data Importer."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Use the instance name as unique_id to allow multiple instances
            # but prevent duplicate names
            instance_name = user_input.get(CONF_INSTANCE_NAME, "default")
            await self.async_set_unique_id(f"{DOMAIN}_{instance_name}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=instance_name, data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_INSTANCE_NAME, default="Energy Data Importer"): cv.string,
                }
            ),
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/patrickvorgers/Home-Assistant-Import-Energy-Data"
            },
        )

