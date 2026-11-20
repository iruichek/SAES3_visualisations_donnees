import numpy as np
import pandas as pd

df = pd.read_csv("data/clean/tgv_meteo.csv", sep=";")

# 1. Lignes avec météo, avec des trains prévus, mois météo complet
base = df[df["ville"].notna() & ~df["prevu_nul"] & (df["mois_complet"] == 1)].copy()
base["taux"] = base["nb_train_retard_arrivee"] / base["nb_train_prevu"]

# 2. Taux "relatif" : on enlève l'effet de la liaison, puis l'effet national du mois
liaison = ["gare_depart", "gare_arrivee"]
base["taux_rel"] = base["taux"] - base.groupby(liaison)["taux"].transform("mean")
base["taux_rel"] -= base.groupby("mois_date")["taux_rel"].transform("mean")

# 3. Une ligne par (ville, mois)
VARS = ["precip_cumul_mm", "rafale_max_kmh", "temp_moy_c", "nb_jours_gel",
        "nb_jours_neige", "nb_jours_vent_fort", "nb_jours_forte_pluie",
        "nb_jours_canicule"]
agg = base.groupby(["ville_depart", "mois_date"], as_index=False).agg(
    taux_rel=("taux_rel", "mean"), **{v: (v, "first") for v in VARS})
agg["mois_num"] = pd.to_datetime(agg["mois_date"]).dt.month

# 4. Écart à la normale (même ville, même mois de l'année)
for v in VARS:
    agg[v + "_ecart"] = agg[v] - agg.groupby(["ville_depart", "mois_num"])[v].transform("mean")


def comparer(serie, y):
    q10, q90 = serie.quantile(0.10), serie.quantile(0.90)
    bas = y[serie <= q10]
    haut = y[serie >= q90] if q90 > q10 else y[serie > q10]
    diff = haut.mean() - bas.mean()
    t = diff / np.sqrt(haut.var() / len(haut) + bas.var() / len(bas))
    return {"n_bas": len(bas), "n_haut": len(haut),
            "taux_bas (pts)": round(bas.mean() * 100, 2),
            "taux_haut (pts)": round(haut.mean() * 100, 2),
            "ecart (pts)": round(diff * 100, 2), "t": round(t, 2)}


print("Mois analysés (ville x mois) :", len(agg))
for titre, suffixe in (("VALEUR BRUTE", ""), ("ECART A LA NORMALE (même ville, même mois de l'année)", "_ecart")):
    res = pd.DataFrame({v: comparer(agg[v + suffixe], agg["taux_rel"]) for v in VARS}).T
    print("\n=== " + titre + " ===")
    print(res.to_string())

print("\nLecture : 'taux' = écart au taux de retard habituel de la liaison, en points de %.")
print("|t| > 2 : écart probablement réel. |t| < 2 : indistinguable du hasard.")