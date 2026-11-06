import sys
import pandas as pd

raw = pd.read_csv("data/raw/tgv_complet.csv", sep=";")
clean = pd.read_csv("data/clean/tgv_clean.csv", sep=";")

cle = ["date", "service", "gare_depart", "gare_arrivee"]
colonnes = ["nb_train_prevu", "nb_annulation", "nb_train_retard_arrivee"]

# Le nettoyage met le texte en majuscules : on fait pareil sur le brut avant de comparer
for col in ["service", "gare_depart", "gare_arrivee"]:
    raw[col] = raw[col].str.strip().str.upper()

m = raw.merge(clean, on=cle, suffixes=("_raw", "_clean"))
print("Lignes retrouvées entre raw et clean :", len(m), "/", len(raw))

echec = len(m) != len(raw)
for c in colonnes:
    diff = (m[c + "_raw"] != m[c + "_clean"]).sum()
    print(f"  {c} : {diff} différences entre raw et clean")
    echec = echec or diff > 0

print("\n5 lignes à vérifier sur le site SNCF :\n")
print(raw.sample(5, random_state=1)[cle + colonnes].to_string(index=False))

if echec:
    print("\nERREUR : le nettoyage a perdu ou modifié des lignes.")
    sys.exit(1)