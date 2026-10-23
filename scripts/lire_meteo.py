import json
import pandas as pd

with open("data/raw/meteo_lyon_2024-01.json", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data["daily"])
print(df.head())
print(df.shape)