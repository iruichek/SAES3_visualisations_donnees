import pandas as pd

df = pd.read_csv("data/raw/tgv_complet.csv", sep=";")

print("1. Valeurs manquantes par colonne")
print(df.isna().sum().to_string())

print("\n2. Lignes en doublon (même mois, service, départ, arrivée)")
cle = ["date", "service", "gare_depart", "gare_arrivee"]
print(df.duplicated(subset=cle).sum())

print("\n3. Colonnes suspectes identiques ?")
a = df["retard_moyen_trains_retard_sup15"]
b = df["retard_moyen_tous_trains_arrivee"]
print("Lignes où elles sont égales :", (a == b).sum(), "/", len(df))

print("\n4. Incohérences")
print("Annulations > trains prévus :", (df["nb_annulation"] > df["nb_train_prevu"]).sum())
print("Retards > trains prévus :", (df["nb_train_retard_arrivee"] > df["nb_train_prevu"]).sum())
print("Valeurs négatives :", (df.select_dtypes("number") < 0).sum().sum())

print("\n5. Statistiques")
print(df[["duree_moyenne", "nb_train_prevu", "nb_annulation",
          "retard_moyen_arrivee"]].describe().to_string())