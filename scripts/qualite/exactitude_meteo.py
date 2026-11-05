# scripts/qualite/exactitude_meteo.py
# Exactitude de la météo : (a) le nettoyage a-t-il altéré les valeurs brutes ?
# (b) échantillon de 5 (ville, mois) à comparer à la main avec une source externe.
# Lancer depuis la racine : python scripts/qualite/exactitude_meteo.py
import sys
import os
import glob
import json
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DOSSIER_RAW, DOSSIER_CLEAN

# Mêmes noms que dans nettoyage_meteo.py (étape 8)
RENOMMAGE = {
    "temperature_2m_max": "temp_max_c", "temperature_2m_min": "temp_min_c",
    "temperature_2m_mean": "temp_moy_c", "precipitation_sum": "precip_mm",
    "rain_sum": "pluie_mm", "snowfall_sum": "neige_cm",
    "wind_speed_10m_max": "vent_max_kmh", "wind_gusts_10m_max": "rafale_max_kmh",
    "weather_code": "code_meteo",
}
TOLERANCE = 1e-9

# =====================================================================
# (a) Comparaison raw / clean
# Pourquoi : prouver que le nettoyage n'a modifié aucune valeur en dehors
# des étapes prévues (interpolation des températures, aberrants -> NaN).
# Toute différence affichée ici doit pouvoir s'expliquer par l'une d'elles.
# =====================================================================
print("=== (a) COMPARAISON RAW / CLEAN ===")
morceaux = []
for chemin in sorted(glob.glob(os.path.join(DOSSIER_RAW, "meteo_*.json"))):
    try:
        with open(chemin, encoding="utf-8") as f:
            brut = json.load(f)
    except json.JSONDecodeError:
        continue
    if not (isinstance(brut, dict) and "reponse_api" in brut):
        continue   # ex. meteo_lyon_2024-01.json (test d'exploration)
    m = pd.DataFrame(brut["reponse_api"]["daily"]).rename(columns={"time": "date"})
    m.insert(0, "ville", brut["ville"])
    morceaux.append(m)

if not morceaux:
    sys.exit("ERREUR : aucun JSON de collecte dans data/raw/.")
raw = pd.concat(morceaux, ignore_index=True).rename(columns=RENOMMAGE)
chemin_jour = os.path.join(DOSSIER_CLEAN, "meteo_jour.csv")
if not os.path.exists(chemin_jour):
    sys.exit(f"ERREUR : {chemin_jour} introuvable. Lance d'abord le nettoyage.")
clean = pd.read_csv(chemin_jour, sep=";", encoding="utf-8")
print(f"Lignes brutes : {len(raw)} ({raw['ville'].nunique()} villes) ; "
      f"lignes propres : {len(clean)} ({clean['ville'].nunique()} villes)")

fusion = raw.merge(clean, on=["ville", "date"], how="outer",
                   suffixes=("_raw", "_clean"), indicator=True)
seulement_raw = fusion[fusion["_merge"] == "left_only"]
seulement_clean = fusion[fusion["_merge"] == "right_only"]
if len(seulement_raw):
    villes = sorted(seulement_raw["ville"].unique())
    print(f"Lignes brutes absentes du clean : {len(seulement_raw)} "
          f"(villes : {villes}) -> relance le nettoyage si tu as collecté depuis.")
print(f"Lignes propres sans équivalent brut (jours ajoutés à l'étape 5a) : {len(seulement_clean)}")

both = fusion[fusion["_merge"] == "both"]
total_diff = 0
for col in RENOMMAGE.values():
    a = both[col + "_raw"].astype(float)
    b = both[col + "_clean"].astype(float)
    meme_nan = a.isna() & b.isna()
    egal = (a - b).abs() <= TOLERANCE
    diff = ~(meme_nan | egal)
    total_diff += int(diff.sum())
    print(f"  {col:<15} valeurs modifiées : {int(diff.sum())}")
    if diff.any():
        print(both.loc[diff, ["ville", "date", col + "_raw", col + "_clean"]].head(5).to_string(index=False))

print(f"Total de valeurs modifiées : {total_diff}")
if total_diff == 0:
    print("-> Aucune valeur brute altérée (cohérent : 0 interpolation, 0 aberrant au nettoyage).")
else:
    print("-> À EXPLIQUER : chaque différence doit venir d'une interpolation (température) "
          "ou d'une mise à NaN d'aberrant.")

# =====================================================================
# (b) Échantillon à comparer à la main avec une source externe
# Pourquoi : la comparaison raw/clean ne prouve PAS l'exactitude (les deux
# viennent de la même source). Seule une source externe indépendante le peut.
# Échantillon : 4 mois remarquables (faciles à retrouver dans les bulletins
# climatiques) + 1 mois tiré au hasard (graine fixe, reproductible).
# =====================================================================
print("\n=== (b) ÉCHANTILLON À VÉRIFIER À LA MAIN ===")
mois = pd.read_csv(os.path.join(DOSSIER_CLEAN, "meteo_mois.csv"), sep=";", encoding="utf-8")
choix = []
if "nb_jours_neige_marquee" in mois.columns:
    choix.append(("mois avec le plus de neige (>= 1 cm)", mois["nb_jours_neige_marquee"].idxmax()))
choix.append(("mois le plus chaud (canicule)", mois["nb_jours_canicule"].idxmax()))
choix.append(("mois le plus pluvieux", mois["precip_cumul_mm"].idxmax()))
choix.append(("mois avec la plus forte rafale", mois["rafale_max_kmh"].idxmax()))
hasard = mois.drop(index=[i for _, i in choix]).sample(1, random_state=42).index[0]
choix.append(("mois tiré au hasard (graine 42)", hasard))

cols = [c for c in ["ville", "mois_date", "temp_moy_c", "precip_cumul_mm", "pluie_cumul_mm",
                    "rafale_max_kmh", "nb_jours_gel", "nb_jours_canicule",
                    "nb_jours_neige", "nb_jours_neige_marquee"] if c in mois.columns]
echantillon = mois.loc[[i for _, i in choix], cols].copy()
echantillon.insert(0, "motif", [m for m, _ in choix])
echantillon["valeur_source_externe"] = ""
echantillon["ecart"] = ""
echantillon["commentaire"] = ""
print(echantillon[cols].to_string(index=False))

os.makedirs("docs", exist_ok=True)
sortie = os.path.join("docs", "echantillon_exactitude_meteo.csv")
echantillon.to_csv(sortie, sep=";", encoding="utf-8", index=False)
print(f"\nÉchantillon enregistré (colonnes à remplir à la main) : {sortie}")
print("À comparer avec les relevés Météo-France ou Infoclimat : température moyenne, "
      "cumul de pluie, rafale max, jours de gel/neige du mois.")
print("Attention : ERA5 = point de grille, les stations donnent d'autres valeurs. "
      "Un écart modéré est normal ; note-le et commente-le au lieu de le cacher.")

sys.exit(1 if total_diff else 0)