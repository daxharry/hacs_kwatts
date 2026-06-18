"""Binary sensor pour l'intégration Kwatts."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    """Configure le binary sensor Kwatts."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["kwatts"]
    async_add_entities([KwattsGoodDaySensor(coordinator, entry)])


class KwattsGoodDaySensor(KwattsEntityMixin, CoordinatorEntity, BinarySensorEntity):
    """Indique si c'est un jour favorable pour la consommation solaire."""

    _attr_name = "Kwatts - Jour favorable"
    _attr_unique_id = "kwatts_good_day"
    _attr_icon = "mdi:solar-power"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data:
            try:
                code = self.coordinator.data.get("code")
                return int(code) >= 1 if code is not None else None
            except (ValueError, TypeError):
                return None
        return None
