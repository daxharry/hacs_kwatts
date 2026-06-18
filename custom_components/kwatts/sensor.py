"""Capteurs (sensors) pour l'intégration Kwatts."""
from __future__ import annotations

import time

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import KwattsEntityMixin
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configure les capteurs Kwatts."""
    coordinators = hass.data[DOMAIN][entry.entry_id]
    coordinator = coordinators["kwatts"]
    epex_coordinator = coordinators["epex"]

    async_add_entities([
        KwattsStatusSensor(coordinator, entry),
        KwattsColorSensor(coordinator, entry),
        KwattsCodeSensor(coordinator, entry),
        KwattsEstimatedPriceSensor(coordinator, entry),
        KwattsAdviceSensor(coordinator, entry),
        KwattsDateSensor(coordinator, entry),
        KwattsEpexPriceSensor(epex_coordinator, entry),
    ])


class KwattsBaseSensor(KwattsEntityMixin, CoordinatorEntity, SensorEntity):
    """Classe de base pour les capteurs Kwatts."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry


class KwattsStatusSensor(KwattsBaseSensor):
    """Statut de l'intégration Kwatts."""

    _attr_name = "Kwatts - Statut"
    _attr_unique_id = "kwatts_status"
    _attr_icon = "mdi:information-outline"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        if not self.coordinator.last_update_success:
            return "Erreur"
        if not self.coordinator.data:
            return "Inconnu"
        if self.coordinator.data.get("waiting"):
            return "En attente de prix"
        if self.coordinator.data.get("color"):
            return "Prix disponibles"
        return "Données manquantes"


class KwattsColorSensor(KwattsBaseSensor):
    """Couleur du jour Kwatts."""

    _attr_name = "Kwatts - Couleur du jour"
    _attr_unique_id = "kwatts_color_today"
    _attr_icon = "mdi:traffic-light"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("color")


class KwattsCodeSensor(KwattsBaseSensor):
    """Code du jour Kwatts."""

    _attr_name = "Kwatts - Code du jour"
    _attr_unique_id = "kwatts_code_today"
    _attr_icon = "mdi:numeric"

    @property
    def native_value(self):
        if self.coordinator.data:
            try:
                code = self.coordinator.data.get("code")
                return int(code) if code is not None else None
            except (ValueError, TypeError):
                return None
        return None


class KwattsEstimatedPriceSensor(KwattsBaseSensor):
    """Prix estimé du jour Kwatts."""

    _attr_name = "Kwatts - Prix estimé du jour"
    _attr_unique_id = "kwatts_estimated_price_today"
    _attr_icon = "mdi:currency-eur"
    _attr_native_unit_of_measurement = "€/MWh"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        if self.coordinator.data:
            try:
                price = self.coordinator.data.get("estimatedPrice")
                return float(price) if price is not None else None
            except (ValueError, TypeError):
                return None
        return None


class KwattsAdviceSensor(KwattsBaseSensor):
    """Conseil du jour Kwatts."""

    _attr_name = "Kwatts - Conseil du jour"
    _attr_unique_id = "kwatts_advice_today"
    _attr_icon = "mdi:message-text"

    @property
    def native_value(self):
        return self.coordinator.data.get("advice") if self.coordinator.data else None


class KwattsDateSensor(KwattsBaseSensor):
    """Date du jour Kwatts."""

    _attr_name = "Kwatts - Date"
    _attr_unique_id = "kwatts_time_today"
    _attr_icon = "mdi:calendar-today"

    @property
    def native_value(self):
        return self.coordinator.data.get("time") if self.coordinator.data else None


class KwattsEpexPriceSensor(KwattsBaseSensor):
    """Prix EPEX Spot actuel pour la France (Energy-Charts)."""

    _attr_name = "Kwatts - Prix EPEX Spot"
    _attr_unique_id = "kwatts_epex_price"
    _attr_icon = "mdi:lightning-bolt"
    _attr_native_unit_of_measurement = "€/kWh"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 4

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data:
            return None
        timestamps = data.get("unix_seconds", [])
        prices = data.get("price", [])
        if not timestamps or not prices:
            return None

        now = int(time.time())
        current_price = None

        for i in range(len(timestamps) - 1):
            if timestamps[i] <= now < timestamps[i + 1]:
                current_price = prices[i]
                break
        else:
            if timestamps and now >= timestamps[-1]:
                current_price = prices[-1]

        if current_price is None:
            return None

        # Conversion EUR/MWh → €/kWh
        return round(current_price / 1000, 6)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}
        return {"source": "Energy-Charts.info", "zone": "FR (EPEX Spot)"}
