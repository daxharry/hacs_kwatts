# Kwatts for Home Assistant

<p align="center">
  <img src="icon.png" alt="Kwatts" width="128" height="128">
</p>

Unofficial **Kwatts** integration for Home Assistant.

It queries the Kwatts API with your API key and exposes the day color, estimated price, advice, favorable-day indicator, and availability status. It also adds a France EPEX Spot price sensor via Energy-Charts.info.

This HACS integration is installed directly from the repository content, without a GitHub release.

## Created entities

- 🟢🟠🔴 **Day color**
- 🔢 **Day code**
- 💶 **Estimated price (€/MWh)**
- 💬 **Daily advice**
- 📅 **Date**
- ⚡ **France EPEX Spot price**
- ℹ️ **Integration status**
- ☀️ **Favorable day** *(binary sensor)*

## Icon

- HACS and Home Assistant use `custom_components/kwatts/brand/icon.png` and `custom_components/kwatts/brand/logo.png`.
- Root `icon.png` is only used to display this page.
- Entities have dedicated `mdi:*` icons.

## API key

Get your key at [apps.kwatts.fr/advices](https://apps.kwatts.fr/advices)
