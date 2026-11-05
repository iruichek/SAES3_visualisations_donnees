# scripts/config.py
# Constantes partagées par tous les scripts (collecte, nettoyage, qualité).
# Scripts lancés depuis la RACINE du dépôt : chemins relatifs.

# --- API Open-Meteo (archive historique) ---
URL_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
VARIABLES_DAILY = [
    "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
    "precipitation_sum", "rain_sum", "snowfall_sum",
    "wind_speed_10m_max", "wind_gusts_10m_max", "weather_code",
]
DATE_DEBUT = "2018-01-01"
DATE_FIN = "2026-09-30"
TIMEZONE = "Europe/Paris"

# --- Dossiers ---
DOSSIER_RAW = "data/raw"
DOSSIER_CLEAN = "data/clean"

# --- Réseau / quotas ---
TIMEOUT_S = 60                  # délai max d'une requête
NB_TENTATIVES = 3               # nombre d'essais par requête
PAUSE_RETRY_S = 5               # pause (x numéro d'essai) après une erreur réseau/serveur
PAUSE_ENTRE_APPELS_S = 30       # pause entre deux villes (à augmenter si 429 trop fréquents)
ATTENTE_429_MINUTE_S = 65       # attente si limite par minute atteinte
ATTENTE_429_HEURE_S = 3660      # attente si limite par heure atteinte

# --- Nettoyage (PROPOSITIONS, à valider à l'étape nettoyage et à justifier) ---
PLAGES_PHYSIQUES = {            # (min, max) plausibles pour la France
    "temperature_2m_max": (-40, 50), "temperature_2m_min": (-40, 50),
    "temperature_2m_mean": (-40, 50),
    "precipitation_sum": (0, 400), "rain_sum": (0, 400),
    "snowfall_sum": (0, 150),   # cm, à vérifier
    "wind_speed_10m_max": (0, 300), "wind_gusts_10m_max": (0, 300),
}
SEUIL_GEL_C = 0                 # nb_jours_gel : tmin < 0
SEUIL_CANICULE_C = 35           # nb_jours_canicule : tmax >= 35
SEUIL_FORTE_PLUIE_MM = 20       # nb_jours_forte_pluie : precip >= 20
SEUIL_VENT_FORT_KMH = 80        # nb_jours_vent_fort : rafales >= 80
SEUIL_NEIGE_CM = 0              # nb_jours_neige : neige > 0
SEUIL_NEIGE_MARQUEE_CM = 1      # nb_jours_neige_marquee : neige >= 1 cm