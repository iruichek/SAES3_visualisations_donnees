import json
import requests

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 45.76,
    "longitude": 4.84,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "daily": "precipitation_sum",
    "timezone": "Europe/Paris",
}

r = requests.get(url, params=params)
print(r.status_code)

data = r.json()
print(data["daily"]["time"][:3])
print(data["daily"]["precipitation_sum"][:3])

with open("meteo_lyon_2024-01.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Fichier enregistré")