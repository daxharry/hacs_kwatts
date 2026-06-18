# Kwatts pour Home Assistant

<p align="center">
  <img src="icon.png" alt="Kwatts" width="128" height="128">
</p>

Intégration non-officielle des données **Kwatts** dans Home Assistant.

Elle interroge l'API Kwatts avec votre clé API, expose la couleur du jour, le prix estimé, le conseil, l'indicateur de jour favorable et le statut de disponibilité. Elle ajoute aussi un capteur de prix EPEX Spot France via Energy-Charts.info.

Cette intégration HACS s'installe directement depuis le contenu du dépôt, sans release GitHub.

## Entités créées

- 🟢🟠🔴 **Couleur du jour**
- 🔢 **Code du jour**
- 💶 **Prix estimé (€/MWh)**
- 💬 **Conseil du jour**
- 📅 **Date**
- ⚡ **Prix EPEX Spot France**
- ℹ️ **Statut de l'intégration**
- ☀️ **Jour favorable** *(binary sensor)*

## Icône

- HACS et Home Assistant utilisent `custom_components/kwatts/brand/icon.png` et `custom_components/kwatts/brand/logo.png`.
- `icon.png` à la racine sert uniquement à l'affichage de cette page.
- Les entités ont des icônes `mdi:*` dédiées.

## Clé API

Obtenez votre clé sur [apps.kwatts.fr/advices](https://apps.kwatts.fr/advices)
