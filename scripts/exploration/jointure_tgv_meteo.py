import pandas as pd

tgv = pd.read_csv("data/clean/tgv_clean.csv", sep=";")
meteo = pd.read_csv("data/clean/meteo_mois.csv", sep=None, engine="python")

# 1. Une seule ligne météo par (ville, mois) ?
print("Doublons météo (ville, mois) :", meteo.duplicated(subset=["ville", "mois_date"]).sum())
print("Villes météo :", meteo["ville"].nunique(), "| mois :", meteo["mois_date"].nunique())

# 2. Jointure à gauche : on garde toutes les lignes TGV
df = tgv.merge(meteo, how="left",
               left_on=["ville_depart", "mois_date"],
               right_on=["ville", "mois_date"],
               validate="m:1", indicator=True)

a_ville = df["ville_depart"].notna()
a_meteo = df["_merge"] == "both"

print("\nLignes TGV avant :", len(tgv), "| après :", len(df))
print("  sans ville de départ (gare étrangère) :", (~a_ville).sum())
print("  avec ville mais SANS météo :", (a_ville & ~a_meteo).sum())
print("  avec météo :", a_meteo.sum())

# 3. Détail des lignes qui ont une ville mais pas de météo
manque = df[a_ville & ~a_meteo]
if len(manque):
    print("\nVilles et mois sans correspondance :")
    print(manque.groupby("ville_depart")["date"].agg(["min", "max", "count"]).to_string())

# 4. Mois météo incomplets parmi les lignes jointes
print("\nLignes jointes avec un mois météo incomplet :",
      (df.loc[a_meteo, "mois_complet"] == 0).sum())

# 5. Sauvegarde du résultat de contrôle
df.drop(columns="_merge").to_csv("data/clean/tgv_meteo.csv", index=False,
                                 sep=";", encoding="utf-8")

# 6. Premier regard (corrélation, pas causalité)
base = df[a_meteo & ~df["prevu_nul"] & (df["mois_complet"] == 1)].copy()
base["taux_retard"] = base["nb_train_retard_arrivee"] / base["nb_train_prevu"]
cols = ["precip_cumul_mm", "temp_moy_c", "rafale_max_kmh", "nb_jours_gel", "nb_jours_neige"]
print("\nCorrélation avec le taux de retard :")
print(base[["taux_retard"] + cols].corr()["taux_retard"].round(3).to_string())