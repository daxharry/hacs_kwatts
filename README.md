# Kwatts – Intégration Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/daxharry/kwatts.svg)](https://github.com/daxharry/kwatts/releases)

Intégration non-officielle pour [Kwatts](https://apps.kwatts.fr) dans Home Assistant.

Kwatts fournit des conseils quotidiens sur la qualité de la production solaire et les prix de l'électricité, permettant d'optimiser votre consommation.

---

## Fonctionnalités

Cette intégration expose les entités suivantes :

| Entité | Type | Description |
|--------|------|-------------|
| `sensor.kwatts_couleur_du_jour` | Sensor | Couleur du jour (vert / orange / rouge) |
| `sensor.kwatts_code_du_jour` | Sensor | Code numérique du jour |
| `sensor.kwatts_prix_estime_du_jour` | Sensor | Prix estimé en €/MWh |
| `sensor.kwatts_conseil_du_jour` | Sensor | Conseil textuel du jour |
| `sensor.kwatts_date` | Sensor | Date de la donnée |
| `sensor.kwatts_statut` | Sensor | Statut de l'intégration (voir ci-dessous) |
| `sensor.kwatts_prix_epex_spot` | Sensor | Prix EPEX Spot actuel en €/kWh (France, Energy-Charts) |
| `binary_sensor.kwatts_jour_favorable` | Binary Sensor | `on` si le jour est favorable (code ≥ 1) |

Les données Kwatts sont actualisées **toutes les heures par défaut** (configurable). Le prix EPEX Spot est mis à jour toutes les **15 minutes** (slots de marché).

Le sensor **Statut** reflète l'état de l'intégration en temps réel :

| Valeur | Signification |
|--------|---------------|
| `Prix disponibles` | Les données du jour sont reçues normalement |
| `En attente de prix` | Normal en début de journée, l'API n'a pas encore publié les prix |
| `Données manquantes` | Les prix ont disparu après avoir été reçus — anomalie côté API |
| `Erreur` | Problème de connexion à l'API |

> **Note :** En début de journée, les données peuvent ne pas encore être disponibles. Le sensor "Couleur du jour" affiche alors **"En attente de prix"** et les autres entités restent disponibles avec des valeurs vides — c'est un comportement normal. Si les données deviennent à nouveau indisponibles après avoir été reçues, un avertissement est enregistré dans les logs Home Assistant.

---

## Installation via HACS

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur **Intégrations** → ⋮ → **Dépôts personnalisés**
3. Ajoutez l'URL : `https://github.com/daxharry/kwatts`
4. Catégorie : **Intégration**
5. Cliquez sur **Télécharger**
6. Redémarrez Home Assistant

## Installation manuelle

1. Copiez le dossier `custom_components/kwatts/` dans votre répertoire `/config/custom_components/`
2. Redémarrez Home Assistant

---

## Configuration

1. Allez dans **Paramètres → Appareils & Services → Ajouter une intégration**
2. Recherchez **Kwatts**
3. Entrez votre clé API disponible sur [apps.kwatts.fr/advices](https://apps.kwatts.fr/advices)

### Prix EPEX Spot

Le sensor `kwatts_prix_epex_spot` affiche le prix de marché brut de l'électricité pour la France, fourni par [Energy-Charts.info](https://energy-charts.info) :

- Source : EPEX Spot, zone FR
- Unité : **€/kWh** (converti depuis EUR/MWh)
- Mise à jour : toutes les 15 minutes
- Prix brut, sans surcharge ni taxe

---

## Options

Après l'installation, vous pouvez modifier l'intervalle de mise à jour :

1. Allez dans **Paramètres → Appareils & Services → Kwatts**
2. Cliquez sur **Configurer**
3. Définissez l'intervalle souhaité (en minutes)

> **Limite API :** L'API Kwatts est limitée à **40 requêtes par jour**. L'intervalle conseillé est de **60 minutes** (24 requêtes/jour). La valeur minimale autorisée est de 60 minutes.

---

## Prérequis

- Home Assistant ≥ 2023.1.0
- Un compte Kwatts avec une clé API valide

---

## Licence

MIT License
