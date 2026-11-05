# scripts/run_pipeline.py
# Orchestration : collecte météo -> nettoyage météo -> contrôles météo
# (+ scripts TGV existants en option). S'arrête au premier échec.
#
# Exemples (depuis la racine du dépôt) :
#   python scripts/run_pipeline.py                  # pipeline météo complet
#   python scripts/run_pipeline.py --sans-collecte  # ne relance pas la collecte
#   python scripts/run_pipeline.py --avec-tgv       # TGV puis météo
#   python scripts/run_pipeline.py --partiel        # accepte une collecte incomplète
import sys
import json
import glob
import os
import argparse
import subprocess
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent   # racine du dépôt
sys.path.append(str(Path(__file__).resolve().parent))
from gares import GARES
from config import DOSSIER_RAW

parser = argparse.ArgumentParser(description="Pipeline de données SAÉ (météo, TGV en option)")
parser.add_argument("--sans-collecte", action="store_true",
                    help="ne pas lancer la collecte météo")
parser.add_argument("--avec-tgv", action="store_true",
                    help="lancer aussi les scripts TGV existants avant la météo")
parser.add_argument("--partiel", action="store_true",
                    help="continuer même si la collecte est incomplète / les contrôles signalent "
                         "des problèmes (utile pendant la collecte étalée sur plusieurs jours)")
args = parser.parse_args()

# Pourquoi cette fonction : savoir si la collecte est déjà complète, pour ne pas
# relancer 47 appels API inutilement (quota limité).
def nb_json_meteo_valides():
    n = 0
    for chemin in glob.glob(str(RACINE / DOSSIER_RAW / "meteo_*.json")):
        try:
            with open(chemin, encoding="utf-8") as f:
                if "reponse_api" in json.load(f):
                    n += 1
        except (json.JSONDecodeError, OSError):
            pass
    return n


def lancer(nom, script, bloquant=True):
    """Lance un script avec le même Python (celui du venv), depuis la racine.
    Renvoie True si OK. S'arrête avec un message clair si échec bloquant."""
    print(f"\n{'=' * 60}\n>>> {nom}  ({script})\n{'=' * 60}", flush=True)
    code = subprocess.run([sys.executable, script], cwd=RACINE).returncode
    if code == 0:
        print(f">>> {nom} : OK")
        return True
    if bloquant:
        sys.exit(f"\nÉCHEC à l'étape « {nom} » (code {code}). Pipeline arrêté. "
                 f"Corrige le problème puis relance.")
    print(f">>> {nom} : problème signalé (code {code}), on continue (--partiel)")
    return False


# --- Étapes TGV (optionnelles, scripts existants de ton coéquipier) ---
if args.avec_tgv:
    lancer("Collecte TGV", "scripts/collecte/collecte_tgv.py")
    lancer("Nettoyage TGV", "scripts/nettoyage/nettoyage_tgv.py")
    lancer("Contrôles TGV", "scripts/qualite/controles_tgv.py")
    lancer("Exactitude TGV", "scripts/qualite/exactitude_tgv.py")

# --- Étape 1 : collecte météo ---
nb_villes = len({ville for ville, _, _ in GARES.values()})
nb_json = nb_json_meteo_valides()
if args.sans_collecte:
    print(f"\nCollecte météo ignorée (--sans-collecte). JSON bruts valides : {nb_json}/{nb_villes}")
elif nb_json >= nb_villes:
    print(f"\nCollecte météo ignorée : les {nb_json} JSON bruts existent déjà.")
else:
    print(f"\nJSON bruts valides : {nb_json}/{nb_villes} -> collecte lancée "
          f"(les villes déjà collectées sont sautées).")
    lancer("Collecte météo", "scripts/collecte/collecte_meteo.py", bloquant=not args.partiel)

# --- Étape 2 : nettoyage météo ---
lancer("Nettoyage météo", "scripts/nettoyage/nettoyage_meteo.py")

# --- Étape 3 : contrôles qualité météo ---
lancer("Contrôles météo", "scripts/qualite/controles_meteo.py", bloquant=not args.partiel)

print("\nPipeline terminé.")