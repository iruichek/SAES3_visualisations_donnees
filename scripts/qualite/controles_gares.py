import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from gares import GARES, ETRANGERES

df = pd.read_csv("data/raw/tgv_complet.csv", sep=";")
toutes = set(df["gare_depart"].str.strip().str.upper()) | set(
    df["gare_arrivee"].str.strip().str.upper())

sans_correspondance = sorted(toutes - set(GARES) - set(ETRANGERES))
inutiles = sorted((set(GARES) | set(ETRANGERES)) - toutes)

print("Gares sans correspondance dans gares.py :", sans_correspondance)
print("Gares de gares.py absentes du dataset :", inutiles)

depart = df["gare_depart"].str.strip().str.upper()
print("Lignes avec météo possible :", depart.isin(GARES).sum(), "/", len(df))
print("Villes distinctes :", len({v[0] for v in GARES.values()}))

if sans_correspondance:
    print("\nERREUR : ajoute ces gares dans gares.py (GARES ou ETRANGERES).")
    sys.exit(1)
if inutiles:
    print("\nALERTE : gares.py contient des gares absentes du dataset (non bloquant).")