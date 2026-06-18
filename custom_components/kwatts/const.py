"""Constantes pour l'intégration Kwatts."""

DOMAIN = "kwatts"
API_URL = "https://apps.kwatts.fr/api_front/solar/kwattsColorOfToday?key={key}"
EPEX_API_URL = "https://api.energy-charts.info/price?bzn=FR"
SCAN_INTERVAL = 60          # intervalle par défaut en minutes (1 heure)
MIN_SCAN_INTERVAL = 60      # minimum en minutes (conseillé, 40 requêtes/jour max)
CONF_SCAN_INTERVAL = "scan_interval"
