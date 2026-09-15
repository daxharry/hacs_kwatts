# Kwatts – Home Assistant integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Unofficial [Kwatts](https://apps.kwatts.fr) integration for Home Assistant.

## Purpose

This integration adds Kwatts to Home Assistant to track daily signals that help optimize electricity use: day color, code, estimated price, advice, availability status, and France EPEX Spot price.

It queries the Kwatts API with your API key, creates the corresponding Home Assistant entities, and refreshes data on the configured interval. The EPEX Spot price is fetched separately from Energy-Charts.info.

---

## Features

This integration exposes the following entities:

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.kwatts_couleur_du_jour` | Sensor | Day color (green / orange / red) |
| `sensor.kwatts_code_du_jour` | Sensor | Numeric day code |
| `sensor.kwatts_prix_estime_du_jour` | Sensor | Estimated price in €/MWh |
| `sensor.kwatts_conseil_du_jour` | Sensor | Daily advice text |
| `sensor.kwatts_date` | Sensor | Data date |
| `sensor.kwatts_statut` | Sensor | Integration status (see below) |
| `sensor.kwatts_prix_epex_spot` | Sensor | Current EPEX Spot price in €/kWh (France, Energy-Charts) |
| `binary_sensor.kwatts_jour_favorable` | Binary Sensor | `on` if the day is favorable (code ≥ 1) |

Kwatts data is refreshed **every hour by default** (configurable). The EPEX Spot price is updated every **15 minutes** (market slots).

The **Status** sensor reflects the live state of the integration:

| Value | Meaning |
|--------|---------|
| `Prix disponibles` | Today's data was received normally |
| `En attente de prix` | Normal early in the day; the API has not published prices yet |
| `Données manquantes` | Prices disappeared after they had been received — API-side anomaly |
| `Erreur` | Problem connecting to the API |

> **Note:** Early in the day, data may not be available yet. The "Day color" sensor then shows **"En attente de prix"** and the other entities stay available with empty values — this is expected. If data becomes unavailable again after it was received, a warning is written to the Home Assistant logs.

---

## Installation via HACS

1. Open HACS in Home Assistant
2. Click **Integrations** → ⋮ → **Custom repositories**
3. Add the URL: `https://github.com/daxharry/hacs_kwatts`
4. Category: **Integration**
5. Click **Download**
6. Restart Home Assistant

This HACS integration is installed from the repository branch content, without a GitHub release archive. `hacs.json` therefore sets `zip_release: false`.

## Manual installation

1. Copy the `custom_components/kwatts/` folder into `/config/custom_components/`
2. Restart Home Assistant

---

## Configuration

1. Go to **Settings → Devices & services → Add integration**
2. Search for **Kwatts**
3. Enter your API key from [apps.kwatts.fr/advices](https://apps.kwatts.fr/advices)

### EPEX Spot price

The `kwatts_prix_epex_spot` sensor shows the raw wholesale electricity price for France, provided by [Energy-Charts.info](https://energy-charts.info):

- Source: EPEX Spot, FR zone
- Unit: **€/kWh** (converted from EUR/MWh)
- Update: every 15 minutes
- Raw price, without surcharge or tax

---

## Options

After installation you can change the update interval:

1. Go to **Settings → Devices & services → Kwatts**
2. Click **Configure**
3. Set the desired interval (in minutes)

> **API limit:** The Kwatts API is limited to **40 requests per day**. The recommended interval is **60 minutes** (24 requests/day). The minimum allowed value is 60 minutes.

---

## Requirements

- Home Assistant ≥ 2023.1.0
- A Kwatts account with a valid API key

---

## Icon

- HACS and Home Assistant use the local icons: `custom_components/kwatts/brand/icon.png` and `custom_components/kwatts/brand/logo.png`
- Root `icon.png` is only used for GitHub display (`info.md`)
- Entities also expose `mdi:*` icons in Home Assistant so they stay readable on dashboards

---

## License

MIT License
