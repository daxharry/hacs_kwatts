"""Config flow for the Kwatts integration."""
from __future__ import annotations

import asyncio
import hashlib

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import API_URL, CONF_SCAN_INTERVAL, DOMAIN, MIN_SCAN_INTERVAL, SCAN_INTERVAL


def _api_key_schema(default: str | None = None) -> vol.Schema:
    if default:
        return vol.Schema({vol.Required("api_key", default=default): str})
    return vol.Schema({vol.Required("api_key"): str})


class KwattsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kwatts."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return KwattsOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Initial step: API key."""
        errors = {}

        if user_input is not None:
            api_key = user_input["api_key"].strip()
            if await self._test_api_key(api_key):
                unique_id = hashlib.sha256(api_key.encode()).hexdigest()
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Kwatts",
                    data={"api_key": api_key},
                )
            errors["api_key"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=_api_key_schema(),
            errors=errors,
            description_placeholders={"url": "https://apps.kwatts.fr/advices"},
        )

    async def async_step_reconfigure(self, user_input=None):
        """Allow changing the API key from the Integrations page."""
        errors = {}
        entry = self._reconfigure_entry()

        if user_input is not None:
            api_key = user_input["api_key"].strip()
            if await self._test_api_key(api_key):
                unique_id = hashlib.sha256(api_key.encode()).hexdigest()
                await self.async_set_unique_id(unique_id)
                if hasattr(self, "_abort_if_unique_id_mismatch"):
                    self._abort_if_unique_id_mismatch()
                data = {**dict(entry.data), "api_key": api_key}
                if hasattr(self, "async_update_reload_and_abort"):
                    return self.async_update_reload_and_abort(entry, data=data)
                self.hass.config_entries.async_update_entry(entry, data=data)
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")
            errors["api_key"] = "invalid_auth"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_api_key_schema(entry.data.get("api_key")),
            errors=errors,
            description_placeholders={"url": "https://apps.kwatts.fr/advices"},
        )

    def _reconfigure_entry(self) -> config_entries.ConfigEntry:
        getter = getattr(self, "_get_reconfigure_entry", None)
        if callable(getter):
            return getter()
        entry_id = self.context.get("entry_id")
        entry = self.hass.config_entries.async_get_entry(entry_id)
        if entry is None:
            raise RuntimeError("Kwatts config entry not found")
        return entry

    async def _test_api_key(self, api_key: str) -> bool:
        """Return True when the API key is accepted by Kwatts."""
        session = async_get_clientsession(self.hass)
        url = API_URL.format(key=api_key)
        try:
            async with asyncio.timeout(10):
                async with session.get(url) as response:
                    return response.status not in (401, 403)
        except (TimeoutError, aiohttp.ClientError, asyncio.TimeoutError):
            return False
        except Exception:
            return False


class KwattsOptionsFlow(config_entries.OptionsFlow):
    """Handle Kwatts options (update interval)."""

    def __init__(self, config_entry: config_entries.ConfigEntry | None = None) -> None:
        # Home Assistant 2024.12+ owns config_entry and raises if it is assigned.
        self._config_entry = config_entry

    @property
    def _entry(self) -> config_entries.ConfigEntry:
        return getattr(self, "config_entry", None) or self._config_entry

    async def async_step_init(self, user_input=None):
        """Show the options form."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self._entry.options.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=current_interval
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_SCAN_INTERVAL,
                            max=1440,
                            step=1,
                            unit_of_measurement="minutes",
                            mode=NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
            description_placeholders={
                "max_requests": "40",
                "min_interval": str(MIN_SCAN_INTERVAL),
            },
        )
