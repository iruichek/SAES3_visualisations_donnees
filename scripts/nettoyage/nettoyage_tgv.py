"""nettoyage du brut TGV -> data/clean/tgv_clean.csv """
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from gares import GARES

os.makedirs("data/clean", exist_ok=True)

df = pd.read_csv("data/raw/tgv_complet.csv", sep=";")
print("Lignes au départ :", len(df))

# 1. Supprimer les colonnes vides à 100 %
df = df.drop(columns=["commentaire_annulation", "commentaire_retards_depart"])

# 2. Normaliser le texte
for col in ["service", "gare_depart", "gare_arrivee"]:
    df[col] = df[col].str.strip().str.upper()

# 3. Valeurs impossibles (négatives) -> NULL
for col in ["retard_moyen_arrivee", "retard_moyen_trains_retard_sup15",
            "nb_train_retard_sup_30"]:
    n = (df[col] < 0).sum()
    df.loc[df[col] < 0, col] = np.nan
    print(f"{col} : {n} valeurs négatives mises à NULL")

# 4. Durée de 0 minute -> NULL, et marquer les lignes sans train prévu
n = (df["duree_moyenne"] == 0).sum()
df.loc[df["duree_moyenne"] == 0, "duree_moyenne"] = np.nan
print(f"duree_moyenne : {n} valeurs à 0 mises à NULL")
df["prevu_nul"] = df["nb_train_prevu"] == 0

# 5. Valeurs aberrantes basses (règle IQR) -> NULL
for col in ["retard_moyen_tous_trains_depart", "retard_moyen_tous_trains_arrivee"]:
    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    borne_basse = q1 - 1.5 * (q3 - q1)
    n = (df[col] < borne_basse).sum()
    df.loc[df[col] < borne_basse, col] = np.nan
    print(f"{col} : {n} valeurs sous {borne_basse:.1f} min mises à NULL")

# 6. Préparer le croisement avec la météo
df["ville_depart"] = df["gare_depart"].map(
    lambda g: GARES[g][0] if g in GARES else None)
df["mois_date"] = pd.to_datetime(df["date"] + "-01")
df["annee"] = df["mois_date"].dt.year

# 7. Sauvegarde
df.to_csv("data/clean/tgv_clean.csv", index=False, sep=";", encoding="utf-8")

print("Lignes à la fin :", len(df))
print("Lignes sans ville de départ (météo impossible) :",
      df["ville_depart"].isna().sum())
print("Lignes avec prevu_nul :", df["prevu_nul"].sum())
print("\nMinimum des retards moyens 'tous trains' (à vérifier) :")
print(df[["retard_moyen_tous_trains_depart",
          "retard_moyen_tous_trains_arrivee"]].min().to_string())