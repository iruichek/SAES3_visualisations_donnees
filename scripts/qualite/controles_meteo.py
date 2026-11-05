# scripts/qualite/controles_meteo.py
# Contrôles qualité de la météo : exhaustivité, cohérence, jointure avec le TGV.
# Lancer depuis la racine : python scripts/qualite/controles_meteo.py
import sys
import os
import unicodedata
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from gares import GARES
from config import DATE_DEBUT, DATE_FIN, DOSSIER_CLEAN, PLAGES_PHYSIQUES

TOLERANCE_ARRONDI = 0.1
problemes = []   # liste des problèmes bloquants, pour le code de sortie final


def nfc(texte):
    """Même normalisation d'accents que dans le nettoyage."""
    return unicodedata.normalize("NFC", str(texte).strip())


# ---------------------------------------------------------------------
# 0. Chargement
# ---------------------------------------------------------------------
chemin_jour = os.path.join(DOSSIER_CLEAN, "meteo_jour.csv")
chemin_mois = os.path.join(DOSSIER_CLEAN, "meteo_mois.csv")
chemin_tgv = os.path.join(DOSSIER_CLEAN, "tgv_clean.csv")
for c in (chemin_jour, chemin_mois, chemin_tgv):
    if not os.path.exists(c):
        sys.exit(f"ERREUR : {c} introuvable. Lance d'abord le nettoyage (météo et TGV).")

jour = pd.read_csv(chemin_jour, sep=";", encoding="utf-8")
mois = pd.read_csv(chemin_mois, sep=";", encoding="utf-8")
tgv = pd.read_csv(chemin_tgv, sep=";", encoding="utf-8")
print(f"0. Chargé : meteo_jour {len(jour)} lignes, meteo_mois {len(mois)} lignes, tgv_clean {len(tgv)} lignes")

# =====================================================================
# 1. EXHAUSTIVITÉ
# Pourquoi : vérifier qu'on a toutes les villes et tous les mois attendus,
# sinon des lignes TGV n'auront pas de météo.
# =====================================================================
print("\n=== 1. EXHAUSTIVITÉ ===")
villes_attendues = {nfc(v) for v, _, _ in GARES.values()}
villes_presentes = set(mois["ville"].map(nfc))
manquantes = sorted(villes_attendues - villes_presentes)
en_trop = sorted(villes_presentes - villes_attendues)
print(f"Villes présentes : {len(villes_presentes)}/{len(villes_attendues)}")
if manquantes:
    print(f"  Villes ABSENTES ({len(manquantes)}) : {manquantes}")
    problemes.append(f"{len(manquantes)} ville(s) sans météo (collecte incomplète ?)")
if en_trop:
    print(f"  Villes présentes mais absentes de gares.py : {en_trop}")
    problemes.append("villes météo inconnues de gares.py")

mois_attendus = pd.date_range(DATE_DEBUT, DATE_FIN, freq="MS").strftime("%Y-%m-%d")
print(f"Mois attendus par ville : {len(mois_attendus)} (de {mois_attendus[0]} à {mois_attendus[-1]})")
nb_mois = mois.groupby("ville")["mois_date"].nunique()
incomplets_ville = nb_mois[nb_mois != len(mois_attendus)]
if len(incomplets_ville):
    print(f"  Villes avec un nombre de mois différent de {len(mois_attendus)} :")
    print(incomplets_ville.to_string())
    problemes.append("villes avec des mois manquants")
else:
    print("  Toutes les villes présentes ont les mois attendus.")

mois_non_complets = mois[mois["mois_complet"] == 0]
print(f"Mois incomplets (mois_complet = 0) : {len(mois_non_complets)}")
if len(mois_non_complets):
    print(mois_non_complets[["ville", "mois_date", "nb_jours_mesures"]].head(10).to_string(index=False))
    problemes.append("mois incomplets")

# =====================================================================
# 2. COHÉRENCE
# Pourquoi : on relit les CSV propres et on revérifie les règles physiques,
# indépendamment du script de nettoyage (contrôle de sortie).
# =====================================================================
print("\n=== 2. COHÉRENCE ===")
doublons = jour.duplicated(subset=["ville", "date"]).sum()
print(f"Doublons (ville, date) dans meteo_jour : {doublons}")
if doublons:
    problemes.append("doublons dans meteo_jour")

incoh_temp = ((jour["temp_min_c"] > jour["temp_moy_c"] + TOLERANCE_ARRONDI) |
              (jour["temp_moy_c"] > jour["temp_max_c"] + TOLERANCE_ARRONDI)).sum()
incoh_vent = (jour["rafale_max_kmh"] < jour["vent_max_kmh"]).sum()
incoh_pluie = (jour["pluie_mm"] > jour["precip_mm"] + TOLERANCE_ARRONDI).sum()
print(f"tmin <= tmoy <= tmax violé       : {incoh_temp} ligne(s)")
print(f"rafales >= vent moyen violé      : {incoh_vent} ligne(s)")
print(f"pluie <= précipitations violé    : {incoh_pluie} ligne(s)")
if incoh_temp or incoh_vent or incoh_pluie:
    problemes.append("incohérences physiques dans meteo_jour")

# Plages physiques (mêmes bornes que config.py, noms de colonnes renommés)
PLAGES_RENOMMEES = {
    "temp_max_c": "temperature_2m_max", "temp_min_c": "temperature_2m_min",
    "temp_moy_c": "temperature_2m_mean", "precip_mm": "precipitation_sum",
    "pluie_mm": "rain_sum", "neige_cm": "snowfall_sum",
    "vent_max_kmh": "wind_speed_10m_max", "rafale_max_kmh": "wind_gusts_10m_max",
}
hors_plage = 0
for col, brut in PLAGES_RENOMMEES.items():
    vmin, vmax = PLAGES_PHYSIQUES[brut]
    hors_plage += ((jour[col] < vmin) | (jour[col] > vmax)).sum()
print(f"Valeurs hors plages physiques    : {hors_plage}")
if hors_plage:
    problemes.append("valeurs hors plages dans meteo_jour")

nan_par_col = jour.drop(columns=["ville", "date"]).isna().sum()
nan_par_col = nan_par_col[nan_par_col > 0]
print("Valeurs manquantes (NaN) par colonne :", "aucune" if nan_par_col.empty else "")
if not nan_par_col.empty:
    print(nan_par_col.to_string())

# Cohérence de l'agrégat mensuel
jours_du_mois = pd.to_datetime(mois["mois_date"]).dt.days_in_month
mesures_ko = (mois["nb_jours_mesures"] > jours_du_mois).sum()
compteurs = [c for c in mois.columns if c.startswith("nb_jours_") and c != "nb_jours_mesures"]
compteurs_ko = sum((mois[c] > jours_du_mois).sum() for c in compteurs)
print(f"nb_jours_mesures > jours du mois : {mesures_ko} ; compteurs d'événements > jours du mois : {compteurs_ko}")
if mesures_ko or compteurs_ko:
    problemes.append("agrégat mensuel incohérent")

# =====================================================================
# 3. JOINTURE avec tgv_clean.csv sur (ville_depart, mois_date)
# Pourquoi : c'est le but final. Chaque ligne TGV ayant une ville de départ
# doit trouver une ligne météo ; sinon le graphique croisé perd des données.
# =====================================================================
print("\n=== 3. JOINTURE TGV <-> MÉTÉO ===")
sans_ville = tgv["ville_depart"].isna().sum()
print(f"Lignes TGV sans ville_depart (gares étrangères, normal) : {sans_ville}")

tgv_ville = tgv[tgv["ville_depart"].notna()].copy()
tgv_ville["ville_depart"] = tgv_ville["ville_depart"].map(nfc)
tgv_ville["mois_date"] = tgv_ville["mois_date"].astype(str).str[:10]
print(f"Lignes TGV avec ville_depart : {len(tgv_ville)}")

# Noms de ville du TGV inconnus de gares.py : problème de nom, pas de collecte.
inconnues_gares = sorted(set(tgv_ville["ville_depart"]) - villes_attendues)
if inconnues_gares:
    print(f"  ATTENTION : villes TGV absentes de gares.py : {inconnues_gares}")
    problemes.append("noms de ville TGV incohérents avec gares.py")

cles_meteo = set(zip(mois["ville"].map(nfc), mois["mois_date"].astype(str).str[:10]))
tgv_ville["a_meteo"] = [(v, m) in cles_meteo
                        for v, m in zip(tgv_ville["ville_depart"], tgv_ville["mois_date"])]
sans_meteo = tgv_ville[~tgv_ville["a_meteo"]]
print(f"Lignes TGV SANS ligne météo (ville, mois) : {len(sans_meteo)} / {len(tgv_ville)}")

if len(sans_meteo):
    # Cause 1 : la ville n'a pas encore été collectée.
    ville_non_collectee = ~sans_meteo["ville_depart"].isin(villes_presentes)
    print(f"  dont ville pas encore collectée      : {ville_non_collectee.sum()}")
    print(f"  dont ville collectée, mois manquant  : {(~ville_non_collectee).sum()}  <- vrai problème")
    detail = sans_meteo.groupby("ville_depart").size().sort_values(ascending=False)
    print("  Détail par ville (10 premières) :")
    print(detail.head(10).to_string())
    problemes.append(f"{len(sans_meteo)} ligne(s) TGV sans météo")
else:
    print("  OK : toutes les lignes TGV avec ville ont une ligne météo.")

# Informations utiles pour le rapport
taux = 100 * tgv_ville["a_meteo"].mean() if len(tgv_ville) else 0
print(f"Taux de jointure réussie : {taux:.1f} %")
print("Limite : la jointure ne couvre que la ville de DÉPART ; la ville d'arrivée n'a pas de météo associée.")

# =====================================================================
# Bilan
# =====================================================================
print("\n=== BILAN ===")
if problemes:
    print(f"{len(problemes)} point(s) à traiter :")
    for p in problemes:
        print(f"  - {p}")
    sys.exit(1)   # code non nul : run_pipeline.py pourra s'arrêter
print("Tous les contrôles sont passés.")