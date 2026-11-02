import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
from gares import GARES, ETRANGERES

df = pd.read_csv("data/raw/tgv_complet.csv", sep=";")
toutes = set(df["gare_depart"]) | set(df["gare_arrivee"])

print("Gares sans correspondance :", sorted(toutes - set(GARES) - set(ETRANGERES)))
print("Gares du fichier gares.py absentes du dataset :", sorted((set(GARES) | set(ETRANGERES)) - toutes))

avec_meteo = df["gare_depart"].isin(GARES)
print("Lignes avec météo possible :", avec_meteo.sum(), "/", len(df))
print("Villes distinctes :", len({v[0] for v in GARES.values()}))