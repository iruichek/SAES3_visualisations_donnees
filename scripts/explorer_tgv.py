import pandas as pd

url = "https://data.sncf.com/api/explore/v2.1/catalog/datasets/regularite-mensuelle-tgv-aqst/exports/csv"
df = pd.read_csv(url, sep=";")
df.to_csv("data/raw/tgv_complet.csv", index=False, sep=";", encoding="utf-8")

print(df.shape)
print("Dates :", df["date"].min(), "->", df["date"].max())
print(df["service"].value_counts())

gares = sorted(set(df["gare_depart"]) | set(df["gare_arrivee"]))
print(len(gares), "gares")
for g in gares:
    print(g)