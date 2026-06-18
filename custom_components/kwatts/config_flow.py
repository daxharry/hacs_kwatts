"""Config flow pour l'intégration Kwatts."""
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

from .const import DOMAIN, API_URL, SCAN_INTERVAL, MIN_SCAN_INTERVAL, CONF_SCAN_INTERVAL


class KwattsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère le flux de configuration Kwatts."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return KwattsOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Étape initiale : saisie de la clé API."""
        errors = {}

        if user_input is not None:
            api_key = user_input["api_key"].strip()
            valid = await self._test_api_key(api_key)

            if valid:
                unique_id = hashlib.sha256(api_key.encode()).hexdigest()
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Kwatts",
                    data={"api_key": api_key},
                )
            else:
                errors["api_key"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("api_key"): str,
            }),
            errors=errors,
            description_placeholders={
                "url": "https://apps.kwatts.fr/advices"
            },
        )

    async def _test_api_key(self, api_key: str) -> bool:
        """Vérifie que la clé API est valide en interrogeant l'API."""
        session = async_get_clientsession(self.hass)
        url = API_URL.format(key=api_key)
        try:
            async with asyncio.timeout(10):
                async with session.get(url) as response:
                    return response.status not in (401, 403)
        except Exception:
            return False


class KwattsOptionsFlow(config_entries.OptionsFlow):
    """Gère les options de l'intégration Kwatts."""

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Affiche le formulaire d'options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_SCAN_INTERVAL, default=current_interval): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL,
                        max=1440,
                        step=1,
                        unit_of_measurement="minutes",
                        mode=NumberSelectorMode.BOX,
                    )
                ),
            }),
            description_placeholders={
                "max_requests": "40",
                "min_interval": str(MIN_SCAN_INTERVAL),
            },
        )
