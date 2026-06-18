"""Intégration Kwatts pour Home Assistant."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_URL, EPEX_API_URL, SCAN_INTERVAL, CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configure l'intégration Kwatts depuis une config entry."""
    api_key = entry.data["api_key"]
    session = async_get_clientsession(hass)

    coordinator = KwattsDataUpdateCoordinator(hass, session, api_key, entry)
    await coordinator.async_config_entry_first_refresh()

    epex_coordinator = KwattsEpexCoordinator(hass, session)
    await epex_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "kwatts": coordinator,
        "epex": epex_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Décharge une config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Recharge l'intégration quand les options changent."""
    await hass.config_entries.async_reload(entry.entry_id)


class KwattsDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinateur de mise à jour des données Kwatts."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        api_key: str,
        entry: ConfigEntry,
    ) -> None:
        """Initialise le coordinateur."""
        self.session = session
        self.api_key = api_key
        self.url = API_URL.format(key=api_key)
        self._had_real_data = False

        interval_minutes = entry.options.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=interval_minutes),
        )

    async def _async_update_data(self):
        """Récupère les données depuis l'API Kwatts."""
        try:
            async with asyncio.timeout(10):
                async with self.session.get(self.url) as response:
                    if response.status == 406:
                        if self._had_real_data:
                            _LOGGER.warning(
                                "Kwatts: données de prix manquantes alors que des données étaient disponibles — "
                                "possible problème côté API Kwatts"
                            )
                            return self.data
                        _LOGGER.debug("Kwatts: en attente des prix du jour (normal en début de journée)")
                        return {"waiting": True}
                    response.raise_for_status()
                    data = await response.json()
                    self._had_real_data = True
                    return data
        except aiohttp.ClientResponseError as err:
            raise UpdateFailed(f"Erreur HTTP {err.status}: {err.message}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Erreur de connexion à l'API Kwatts: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Erreur inattendue: {err}") from err


class KwattsEpexCoordinator(DataUpdateCoordinator):
    """Coordinateur pour les prix EPEX Spot France via Energy-Charts."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession) -> None:
        self.session = session
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_epex",
            update_interval=timedelta(minutes=15),
        )

    async def _async_update_data(self):
        """Récupère les prix EPEX Spot depuis Energy-Charts."""
        try:
            async with asyncio.timeout(10):
                async with self.session.get(EPEX_API_URL) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientResponseError as err:
            raise UpdateFailed(f"Erreur HTTP Energy-Charts {err.status}: {err.message}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Erreur de connexion Energy-Charts: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Erreur inattendue EPEX: {err}") from err


class KwattsEntityMixin:
    """Mixin partagé entre tous les entités Kwatts : device_info et available."""

    _entry: ConfigEntry

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Kwatts",
            "manufacturer": "Kwatts",
            "model": "API Solaire",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and self.coordinator.data is not None
