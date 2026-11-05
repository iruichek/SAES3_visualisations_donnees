# scripts/nettoyage/nettoyage_meteo.py
# Nettoyage des données météo : JSON bruts -> meteo_jour.csv + meteo_mois.csv
# Lancer depuis la racine : python scripts/nettoyage/nettoyage_meteo.py
import sys
import os
import glob
import json
import unicodedata
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from gares import GARES
from config import (VARIABLES_DAILY, DATE_DEBUT, DATE_FIN, DOSSIER_RAW,
                    DOSSIER_CLEAN, PLAGES_PHYSIQUES, SEUIL_GEL_C,
                    SEUIL_CANICULE_C, SEUIL_FORTE_PLUIE_MM,
                    SEUIL_VENT_FORT_KMH, SEUIL_NEIGE_CM, SEUIL_NEIGE_MARQUEE_CM)

TOLERANCE_ARRONDI = 0.1   # les valeurs sont arrondies à 0,1 : on tolère cet écart

# ---------------------------------------------------------------------
# 1. Chargement des JSON bruts
# Pourquoi : on part des réponses brutes de l'API (traçabilité), et on
# n'accepte que les fichiers issus de collecte_meteo.py (clé "reponse_api").
# Cela écarte par exemple meteo_lyon_2024-01.json (test d'exploration).
# ---------------------------------------------------------------------
fichiers = sorted(glob.glob(os.path.join(DOSSIER_RAW, "meteo_*.json")))
morceaux, ignores = [], []
for chemin in fichiers:
    try:
        with open(chemin, encoding="utf-8") as f:
            brut = json.load(f)
    except json.JSONDecodeError:
        ignores.append(os.path.basename(chemin))
        continue
    if not (isinstance(brut, dict) and "reponse_api" in brut):
        ignores.append(os.path.basename(chemin))
        continue
    morceau = pd.DataFrame(brut["reponse_api"]["daily"])   # 1 ligne par jour
    morceau.insert(0, "ville", brut["ville"])              # ville exacte de gares.py
    morceaux.append(morceau)

if not morceaux:
    sys.exit("ERREUR : aucun JSON de collecte trouvé dans data/raw/. Lance d'abord collecte_meteo.py.")

df = pd.concat(morceaux, ignore_index=True)
nb_villes = df["ville"].nunique()
print(f"1. Chargement : {len(df)} lignes, {nb_villes} villes ({len(ignores)} fichier(s) ignoré(s) : {ignores})")
if nb_villes != 47:
    print(f"   ATTENTION : {nb_villes} villes sur 47 attendues (collecte incomplète ?)")

# ---------------------------------------------------------------------
# 2. Conversion des types
# Pourquoi : la date doit être un vrai datetime et les mesures des nombres,
# sinon les calculs (moyennes, seuils, jointures) sont faux.
# ---------------------------------------------------------------------
df = df.rename(columns={"time": "date"})
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
for col in VARIABLES_DAILY:
    avant = df[col].isna().sum()
    df[col] = pd.to_numeric(df[col], errors="coerce")
    print(f"2. {col} : {df[col].isna().sum() - avant} valeur(s) non numérique(s) -> NaN")

# ---------------------------------------------------------------------
# 3. Doublons (ville, date)
# Pourquoi : un doublon fausserait les cumuls et les comptages mensuels.
# ---------------------------------------------------------------------
avant = len(df)
df = df.drop_duplicates(subset=["ville", "date"], keep="first")
print(f"3. Doublons (ville, date) supprimés : {avant - len(df)}")

# ---------------------------------------------------------------------
# 4. Normalisation du texte
# Pourquoi : la jointure avec tgv_clean.csv se fait sur le NOM de la ville.
# On GARDE le nom tel que dans gares.py (accents, majuscules), on retire
# seulement les espaces parasites et on uniformise l'encodage des accents
# (NFC : "ç" en un seul caractère), sinon "Besançon" pourrait ne pas matcher.
# ---------------------------------------------------------------------
avant = df["ville"].copy()
df["ville"] = df["ville"].astype(str).str.strip().map(lambda v: unicodedata.normalize("NFC", v))
villes_gares = {unicodedata.normalize("NFC", v) for v, _, _ in GARES.values()}
inconnues = sorted(set(df["ville"]) - villes_gares)
print(f"4. Noms de ville modifiés : {(avant != df['ville']).sum()} ; villes absentes de gares.py : {inconnues}")

# ---------------------------------------------------------------------
# 5. Valeurs manquantes
# a) Calendrier complet : on ajoute les jours absents (lignes vides) pour que
#    "2 jours" signifie bien 2 jours consécutifs.
# b) Interpolation des TEMPÉRATURES uniquement, et seulement pour les trous de
#    2 jours maximum. Pourquoi : la température varie de façon continue, donc
#    interpoler est raisonnable ; la pluie, la neige et le vent sont des
#    événements ponctuels : interpoler inventerait des valeurs.
# ---------------------------------------------------------------------
calendrier = pd.date_range(DATE_DEBUT, DATE_FIN, freq="D")
index_complet = pd.MultiIndex.from_product(
    [sorted(df["ville"].unique()), calendrier], names=["ville", "date"])
avant = len(df)
df = df.set_index(["ville", "date"]).reindex(index_complet).reset_index()
print(f"5a. Jours absents ajoutés (NaN) : {len(df) - avant}")

COLS_TEMP = ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean"]


def interpoler_trous_courts(s, limite=2):
    """Interpole seulement les séquences de NaN de longueur <= limite
    (pandas, avec limit=, remplirait le début des trous plus longs)."""
    interp = s.interpolate(method="linear", limit_area="inside")
    est_nan = s.isna()
    groupe = (~est_nan).cumsum()
    longueur_trou = est_nan.groupby(groupe).transform("sum")
    a_remplir = est_nan & (longueur_trou <= limite)
    return s.where(~a_remplir, interp)


for col in COLS_TEMP:
    avant = df[col].isna().sum()
    df[col] = df.groupby("ville")[col].transform(interpoler_trous_courts)
    print(f"5b. {col} : {avant - df[col].isna().sum()} valeur(s) interpolée(s), "
          f"{df[col].isna().sum()} NaN restant(s)")
print("5c. Pluie, neige, vent : aucune interpolation (NaN conservés)")

# ---------------------------------------------------------------------
# 6. Valeurs aberrantes (plages physiques)
# Pourquoi : on met à NaN (sans supprimer la ligne) ce qui est physiquement
# impossible en France. Plages physiques plutôt qu'IQR : la pluie et le vent
# ont de vrais événements extrêmes (orages, tempêtes) qu'une règle statistique
# supprimerait à tort. Les aberrants mis à NaN ne sont PAS interpolés après
# coup : on n'invente pas de valeur à la place d'une mesure jugée fausse.
# ---------------------------------------------------------------------
for col, (vmin, vmax) in PLAGES_PHYSIQUES.items():
    masque = (df[col] < vmin) | (df[col] > vmax)
    df.loc[masque, col] = float("nan")
    print(f"6. {col} hors [{vmin}, {vmax}] : {masque.sum()} valeur(s) -> NaN")

# ---------------------------------------------------------------------
# 7. Incohérences (signalement, valeurs conservées)
# Pourquoi : détecter des données impossibles (tmin > tmoy...). Choix : on
# SIGNALE sans modifier : ces variables viennent de la même réanalyse, un
# écart ne peut venir que d'arrondis (tolérance 0,1) ou d'un vrai défaut qu'il
# faut examiner à la main avant de décider.
# ---------------------------------------------------------------------
incoh_temp = ((df["temperature_2m_min"] > df["temperature_2m_mean"] + TOLERANCE_ARRONDI) |
              (df["temperature_2m_mean"] > df["temperature_2m_max"] + TOLERANCE_ARRONDI)).sum()
incoh_vent = (df["wind_gusts_10m_max"] < df["wind_speed_10m_max"]).sum()
incoh_pluie = (df["rain_sum"] > df["precipitation_sum"] + TOLERANCE_ARRONDI).sum()
print(f"7. tmin <= tmoy <= tmax violé : {incoh_temp} ligne(s)")
print(f"7. rafales >= vent moyen violé : {incoh_vent} ligne(s)")
print(f"7. pluie <= précipitations totales violé : {incoh_pluie} ligne(s) (contrôle ajouté)")

# ---------------------------------------------------------------------
# 8. Renommage avec les unités
# Pourquoi : noms explicites (unité dans le nom) pour la BdD et l'API.
# ---------------------------------------------------------------------
RENOMMAGE = {
    "temperature_2m_max": "temp_max_c", "temperature_2m_min": "temp_min_c",
    "temperature_2m_mean": "temp_moy_c", "precipitation_sum": "precip_mm",
    "rain_sum": "pluie_mm", "snowfall_sum": "neige_cm",
    "wind_speed_10m_max": "vent_max_kmh", "wind_gusts_10m_max": "rafale_max_kmh",
    "weather_code": "code_meteo",
}
df = df.rename(columns=RENOMMAGE)
df["code_meteo"] = df["code_meteo"].astype("Int64")   # entier, NaN autorisé
df = df.sort_values(["ville", "date"]).reset_index(drop=True)
print(f"8. Colonnes renommées : {len(RENOMMAGE)}")

# ---------------------------------------------------------------------
# 9. Agrégation mensuelle par ville
# Pourquoi : le jeu TGV est mensuel ; on ramène la météo à la même maille
# (ville, mois_date) et on ajoute des indicateurs d'événements extrêmes,
# plus parlants pour le croisement qu'une simple moyenne.
# Un jour est "mesuré" si toutes les variables d'analyse sont présentes ;
# un mois est complet si tous ses jours le sont.
# Limite : un jour NaN ne compte comme aucun événement (sous-estimation
# possible dans un mois incomplet -> filtrer sur mois_complet).
# ---------------------------------------------------------------------
COLS_ANALYSE = ["temp_max_c", "temp_min_c", "temp_moy_c", "precip_mm",
                "pluie_mm", "neige_cm", "vent_max_kmh", "rafale_max_kmh"]
d = df.copy()
d["mois_date"] = d["date"].dt.to_period("M").dt.to_timestamp()
d["nb_jours_du_mois"] = d["date"].dt.days_in_month
d["jour_mesure"] = d[COLS_ANALYSE].notna().all(axis=1)
d["gel"] = d["temp_min_c"] < SEUIL_GEL_C
d["canicule"] = d["temp_max_c"] >= SEUIL_CANICULE_C
d["forte_pluie"] = d["precip_mm"] >= SEUIL_FORTE_PLUIE_MM
d["vent_fort"] = d["rafale_max_kmh"] >= SEUIL_VENT_FORT_KMH
d["neige"] = d["neige_cm"] > SEUIL_NEIGE_CM
d["neige_marquee"] = d["neige_cm"] >= SEUIL_NEIGE_MARQUEE_CM


def somme(s):
    return s.sum(min_count=1)   # tout NaN -> NaN (et non 0)


mois = d.groupby(["ville", "mois_date"], as_index=False).agg(
    precip_cumul_mm=("precip_mm", somme),
    pluie_cumul_mm=("pluie_mm", somme),
    temp_moy_c=("temp_moy_c", "mean"),
    rafale_max_kmh=("rafale_max_kmh", "max"),
    nb_jours_gel=("gel", "sum"),
    nb_jours_canicule=("canicule", "sum"),
    nb_jours_forte_pluie=("forte_pluie", "sum"),
    nb_jours_vent_fort=("vent_fort", "sum"),
    nb_jours_neige=("neige", "sum"),
    nb_jours_mesures=("jour_mesure", "sum"),
    nb_jours_du_mois=("nb_jours_du_mois", "first"),
    nb_jours_neige_marquee=("neige_marquee", "sum"),
)
mois["mois_complet"] = (mois["nb_jours_mesures"] == mois["nb_jours_du_mois"]).astype(int)
mois = mois.drop(columns="nb_jours_du_mois")
mois[["precip_cumul_mm", "pluie_cumul_mm", "temp_moy_c"]] = \
    mois[["precip_cumul_mm", "pluie_cumul_mm", "temp_moy_c"]].round(2)
mois["mois_date"] = mois["mois_date"].dt.strftime("%Y-%m-%d")   # AAAA-MM-01
print(f"9. Agrégation : {len(mois)} lignes (ville, mois) ; "
      f"mois incomplets : {(mois['mois_complet'] == 0).sum()}")

# ---------------------------------------------------------------------
# 10. Sauvegarde
# ---------------------------------------------------------------------
os.makedirs(DOSSIER_CLEAN, exist_ok=True)
jour = df.copy()
jour["date"] = jour["date"].dt.strftime("%Y-%m-%d")
jour.to_csv(os.path.join(DOSSIER_CLEAN, "meteo_jour.csv"), sep=";", encoding="utf-8", index=False)
mois.to_csv(os.path.join(DOSSIER_CLEAN, "meteo_mois.csv"), sep=";", encoding="utf-8", index=False)
print(f"10. Sauvegardé : meteo_jour.csv ({len(jour)} lignes), meteo_mois.csv ({len(mois)} lignes)")