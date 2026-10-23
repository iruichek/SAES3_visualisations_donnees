import requests

url = "https://data.sncf.com/api/explore/v2.1/catalog/datasets/regularite-mensuelle-ter/records"
r = requests.get(url, params={"select": "region", "group_by": "region", "limit": 100})
for ligne in r.json()["results"]:
    print(ligne["region"])