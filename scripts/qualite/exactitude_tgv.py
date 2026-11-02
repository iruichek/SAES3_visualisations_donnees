import pandas as pd

raw = pd.read_csv("data/raw/tgv_complet.csv", sep=";")
clean = pd.read_csv("data/clean/tgv_clean.csv", sep=";")

cle = ["date", "service", "gare_depart", "gare_arrivee"]
colonnes = ["nb_train_prevu", "nb_annulation", "nb_train_retard_arrivee"]

# Contrôle automatique : le nettoyage a-t-il modifié ces 3 colonnes ?
m = raw.merge(clean, on=cle, suffixes=("_raw", "_clean"))
print("Lignes retrouvées entre raw et clean :", len(m), "/", len(raw))
for c in colonnes:
    diff = (m[c + "_raw"] != m[c + "_clean"]).sum()
    print(f"  {c} : {diff} différences entre raw et clean")

# Échantillon à vérifier à la main sur le site
print("\n5 lignes à vérifier sur le site SNCF :\n")
echantillon = raw.sample(5, random_state=1)[cle + colonnes]
print(echantillon.to_string(index=False))