import argparse
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

parser = argparse.ArgumentParser(description="Pipeline TGV (SNCF)")
parser.add_argument("--sans-collecte", action="store_true",
                    help="ne pas re-télécharger le dataset")
args = parser.parse_args()

ETAPES = [
    ("Collecte TGV",       "scripts/collecte/collecte_tgv.py"),
    ("Contrôle des gares", "scripts/qualite/controles_gares.py"),
    ("Nettoyage TGV",      "scripts/nettoyage/nettoyage_tgv.py"),
    ("Contrôles TGV",      "scripts/qualite/controles_tgv.py"),
    ("Exactitude TGV",     "scripts/qualite/exactitude_tgv.py"),
    # ("Import MySQL",     "scripts/import_bdd.py"),   # à ajouter plus tard
]

if args.sans_collecte:
    ETAPES = ETAPES[1:]
    print("Collecte ignorée (--sans-collecte).")

for nom, script in ETAPES:
    print(f"\n{'=' * 60}\n>>> {nom}  ({script})\n{'=' * 60}", flush=True)
    code = subprocess.run([sys.executable, script], cwd=RACINE).returncode
    if code != 0:
        sys.exit(f"\nÉCHEC à l'étape « {nom} » (code {code}). Pipeline arrêté.")
    print(f">>> {nom} : OK")

print("\nPipeline TGV terminé sans erreur.")