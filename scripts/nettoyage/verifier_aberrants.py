import pandas as pd

df = pd.read_csv("data/clean/tgv_clean.csv", sep=";")

colonnes = ["duree_moyenne", "retard_moyen_arrivee",
            "retard_moyen_tous_trains_depart", "retard_moyen_tous_trains_arrivee"]

def bornes(serie):
    q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr

print("1. Méthode globale (toutes liaisons mélangées)")
for col in colonnes:
    bas, haut = bornes(df[col].dropna())
    nb_bas = (df[col] < bas).sum()
    nb_haut = (df[col] > haut).sum()
    print(f"{col}: bornes [{bas:.1f} ; {haut:.1f}] -> {nb_bas} trop bas, {nb_haut} trop haut")

print("\n2. Méthode par liaison")
liaison = ["gare_depart", "gare_arrivee"]
for col in colonnes:
    q1 = df.groupby(liaison)[col].transform(lambda s: s.quantile(0.25))
    q3 = df.groupby(liaison)[col].transform(lambda s: s.quantile(0.75))
    iqr = q3 - q1
    nb_bas = (df[col] < q1 - 1.5 * iqr).sum()
    nb_haut = (df[col] > q3 + 1.5 * iqr).sum()
    print(f"{col}: {nb_bas} trop bas, {nb_haut} trop haut")

print("\nNombre de liaisons distinctes :", df.groupby(liaison).ngroups)
print("Lignes sur 12907 :", len(df))