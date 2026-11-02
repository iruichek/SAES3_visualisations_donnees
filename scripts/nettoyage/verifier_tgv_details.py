import pandas as pd

df = pd.read_csv("data/raw/tgv_complet.csv", sep=";")
num = df.select_dtypes("number")

print("1. Colonnes contenant des valeurs négatives")
neg = (num < 0).sum()
print(neg[neg > 0].to_string())

print("\n2. Lignes avec 0 train prévu :", (df["nb_train_prevu"] == 0).sum())

print("\n3. Annulations > prévus (5 exemples)")
mask = df["nb_annulation"] > df["nb_train_prevu"]
print(df[mask][["date", "gare_depart", "gare_arrivee",
                "nb_train_prevu", "nb_annulation"]].head().to_string())

print("\n4. Durée moyenne = 0 :", (df["duree_moyenne"] == 0).sum())
print("Durée moyenne > 400 min (5 exemples)")
print(df[df["duree_moyenne"] > 400][["date", "service", "gare_depart",
      "gare_arrivee", "duree_moyenne"]].head().to_string())

print("\n5. Retard moyen arrivée négatif (5 exemples)")
print(df[df["retard_moyen_arrivee"] < 0][["date", "gare_depart", "gare_arrivee",
      "nb_train_retard_arrivee", "retard_moyen_arrivee"]].head().to_string())

print("\n6. Colonnes suspectes égales : répartition par année")
egal = df["retard_moyen_trains_retard_sup15"] == df["retard_moyen_tous_trains_arrivee"]
print(df[egal]["date"].str[:4].value_counts().sort_index().to_string())