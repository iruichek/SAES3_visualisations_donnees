import pandas as pd

df = pd.read_csv("data/clean/tgv_clean.csv", sep=";")
c15, c30, c60 = "nb_train_retard_sup_15", "nb_train_retard_sup_30", "nb_train_retard_sup_60"

ok = df[c15].notna() & df[c30].notna() & df[c60].notna()
print("Lignes comparables (sans NULL) :", ok.sum(), "/", len(df))

viol_60_30 = ok & (df[c60] > df[c30])
viol_30_15 = ok & (df[c30] > df[c15])
print("60 > 30 :", viol_60_30.sum())
print("30 > 15 :", viol_30_15.sum())

cols = ["date", "gare_depart", "gare_arrivee", c15, c30, c60]
print("\nExemples 30 > 15")
print(df[viol_30_15][cols].head(8).to_string())

print("\nRépartition par année des violations 30 > 15")
print(df[viol_30_15]["date"].str[:4].value_counts().sort_index().to_string())

print("\nLes 3 colonnes sont-elles souvent égales ?")
print("15 == 30 :", (ok & (df[c15] == df[c30])).sum())
print("30 == 60 :", (ok & (df[c30] == df[c60])).sum())

print("\nMoyennes des 3 colonnes (si cumulatives : 15 > 30 > 60)")
print(df[[c15, c30, c60]].mean().to_string())