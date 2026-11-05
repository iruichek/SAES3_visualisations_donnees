# scripts/collecte/collecte_meteo.py
# Collecte météo journalière (Open-Meteo archive) : 1 appel par VILLE distincte.
# Lancer depuis la racine : python scripts/collecte/collecte_meteo.py
import sys
import os
import json
import time
import unicodedata
from datetime import date
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from gares import GARES
from config import (URL_ARCHIVE, VARIABLES_DAILY, DATE_DEBUT, DATE_FIN,
                    TIMEZONE, DOSSIER_RAW, PAUSE_ENTRE_APPELS_S)
from http_utils import requete_json, ErreurAPI, QuotaJournalierAtteint

# 1. Une seule coordonnée par ville
# Pourquoi : plusieurs gares ont la même ville (Paris x5) mais la jointure se
# fait sur la ville : il faut UNE série météo par ville. On garde la 1re
# occurrence dans l'ordre de gares.py (déterministe).
villes = {}
for gare, (ville, lat, lon) in GARES.items():
    villes.setdefault(ville, (lat, lon))
print(f"1. Villes distinctes : {len(villes)} (attendu : 47)")


def slug(texte):
    """'Besançon' -> 'besancon' (sans accents, minuscules, '_' pour le reste)."""
    sans_accent = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return "".join(c if c.isalnum() else "_" for c in sans_accent.lower()).strip("_")


slugs = {v: slug(v) for v in villes}
assert len(set(slugs.values())) == len(slugs), "Collision de noms de fichiers !"

# Nombre de jours attendus (pour contrôler chaque réponse)
nb_jours_attendus = (date.fromisoformat(DATE_FIN) - date.fromisoformat(DATE_DEBUT)).days + 1
os.makedirs(DOSSIER_RAW, exist_ok=True)

# 2. Boucle de collecte (relançable : on saute les villes déjà collectées)
collectees, deja_la, echecs, non_tentees = [], [], [], []
arret_quota = False

for i, (ville, (lat, lon)) in enumerate(villes.items(), start=1):
    chemin = os.path.join(DOSSIER_RAW, f"meteo_{slugs[ville]}.json")

    if os.path.exists(chemin):
        deja_la.append(ville)
        continue
    if arret_quota:
        non_tentees.append(ville)
        continue

    print(f"2. [{i}/{len(villes)}] {ville} ({lat}, {lon})")
    params = {
        "latitude": lat, "longitude": lon,
        "start_date": DATE_DEBUT, "end_date": DATE_FIN,
        "daily": ",".join(VARIABLES_DAILY),
        "timezone": TIMEZONE,
    }
    try:
        data = requete_json(URL_ARCHIVE, params)
    except QuotaJournalierAtteint as e:
        print(f"   QUOTA JOURNALIER atteint ({e}) -> arrêt, relance demain.")
        arret_quota = True
        non_tentees.append(ville)
        continue
    except ErreurAPI as e:
        print(f"   ÉCHEC : {e}")
        echecs.append(ville)
        continue

    # Pourquoi : une réponse incomplète ne doit pas être enregistrée comme valide.
    daily = data.get("daily", {})
    manquantes = [v for v in VARIABLES_DAILY if v not in daily]
    if manquantes:
        print(f"   ÉCHEC : variables absentes de la réponse : {manquantes}")
        echecs.append(ville)
        continue
    if len(daily.get("time", [])) != nb_jours_attendus:
        print(f"   ATTENTION : {len(daily.get('time', []))} jours reçus, "
              f"{nb_jours_attendus} attendus (à vérifier au nettoyage)")

    # Réponse BRUTE non modifiée + ville exacte (gares.py) + période.
    brut = {
        "ville": ville,
        "periode": {"debut": DATE_DEBUT, "fin": DATE_FIN},
        "reponse_api": data,
    }
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(brut, f, ensure_ascii=False)
    collectees.append(ville)
    print(f"   OK -> {chemin}")
    time.sleep(PAUSE_ENTRE_APPELS_S)   # politesse envers l'API gratuite

# 3. Bilan
print("\n3. BILAN")
print(f"   Collectées maintenant : {len(collectees)}")
print(f"   Déjà présentes        : {len(deja_la)}")
print(f"   Échecs                : {len(echecs)} {echecs}")
print(f"   Non tentées (quota)   : {len(non_tentees)}")
total = len(collectees) + len(deja_la)
print(f"   Total disponible      : {total}/{len(villes)}")
if echecs or non_tentees:
    print("   -> Collecte INCOMPLÈTE : relance le script (les villes déjà faites sont sautées).")
    sys.exit(1)