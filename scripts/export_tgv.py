import json
import requests

url = "https://data.sncf.com/api/explore/v2.1/catalog/datasets/regularite-mensuelle-tgv-aqst/records"
r = requests.get(url, params={"limit": 3})
print(r.status_code)

data = r.json()
print("Total :", data["total_count"])
print(data["results"][0])

with open("data/raw/tgv_echantillon.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Fichier enregistré")