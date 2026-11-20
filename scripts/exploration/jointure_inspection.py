import pandas as pd

tgv = pd.read_csv("data/clean/tgv_clean.csv", sep=";")
meteo = pd.read_csv("data/clean/meteo_mois.csv", sep=None, engine="python")

print("=== TGV ===", tgv.shape)
print(tgv[["date", "mois_date", "ville_depart"]].head(3).to_string())

print("\n=== METEO MOIS ===", meteo.shape)
print(meteo.dtypes.to_string())
print(meteo.head(3).to_string())