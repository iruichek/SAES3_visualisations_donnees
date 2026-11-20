import numpy as np
import pandas as pd

DUREE_MAX = 180                          # minutes : au-delà = longue distance
COVID_DEBUT, COVID_FIN = "2020-03", "2021-06"

VARS = ["precip_cumul_mm", "nb_jours_forte_pluie", "temp_moy_c", "rafale_max_kmh",
        "nb_jours_vent_fort", "nb_jours_neige", "nb_jours_gel", "nb_jours_canicule"]
liaison = ["gare_depart", "gare_arrivee"]

df = pd.read_csv("data/clean/tgv_meteo.csv", sep=";")
meteo = pd.read_csv("data/clean/meteo_mois.csv", sep=None, engine="python")

# 1. Écart à la normale météo (même ville, même mois de l'année), sur tout l'historique
meteo = meteo[meteo["mois_complet"] == 1].copy()
meteo["mois_num"] = pd.to_datetime(meteo["mois_date"]).dt.month
for v in VARS:
    meteo[v + "_ecart"] = meteo[v] - meteo.groupby(["ville", "mois_num"])[v].transform("mean")
ecarts = meteo[["ville", "mois_date"] + [v + "_ecart" for v in VARS]].rename(
    columns={"ville": "ville_depart"})

# 2. Lignes TGV utilisables
base = df[df["ville"].notna() & ~df["prevu_nul"] & (df["mois_complet"] == 1)].copy()
base = base.merge(ecarts, on=["ville_depart", "mois_date"], how="inner")
base["duree_liaison"] = base.groupby(liaison)["duree_moyenne"].transform("median")
base["taux"] = base["nb_train_retard_arrivee"] / base["nb_train_prevu"]

longue = (base["duree_liaison"] > DUREE_MAX) | (base["service"] == "INTERNATIONAL")
covid = base["date"].between(COVID_DEBUT, COVID_FIN)
print(f"Lignes de départ : {len(base)}")
print(f"  longue distance (> {DUREE_MAX} min ou international) : {longue.sum()}")
print(f"  période Covid ({COVID_DEBUT} à {COVID_FIN}) : {covid.sum()}")


def comparer(serie, y):
    """Mois les plus extrêmes (10 % hauts) contre les plus calmes (10 % bas)."""
    q10, q90 = serie.quantile(0.10), serie.quantile(0.90)
    bas = y[serie <= q10]
    haut = y[serie >= q90] if q90 > q10 else y[serie > q10]
    if len(bas) < 30 or len(haut) < 30:
        return np.nan, np.nan
    diff = haut.mean() - bas.mean()
    return diff * 100, diff / np.sqrt(haut.var() / len(haut) + bas.var() / len(bas))


def analyser(sub):
    sub = sub.copy()
    # taux relatif : on retire l'effet de la liaison puis l'effet national du mois
    sub["taux_rel"] = sub["taux"] - sub.groupby(liaison)["taux"].transform("mean")
    sub["taux_rel"] -= sub.groupby("mois_date")["taux_rel"].transform("mean")
    agg = sub.groupby(["ville_depart", "mois_date"], as_index=False).agg(
        taux_rel=("taux_rel", "mean"), **{v + "_ecart": (v + "_ecart", "first") for v in VARS})
    out = {}
    for v in VARS:
        ecart, t = comparer(agg[v + "_ecart"], agg["taux_rel"])
        out[v] = f"{ecart:+.2f} (t={t:+.1f})" if not np.isnan(ecart) else "n/a"
    return len(sub), len(agg), out


scenarios = {
    "1. Toutes": pd.Series(True, index=base.index),
    "2. Sans longue distance": ~longue,
    "3. Sans Covid": ~covid,
    "4. Sans les deux": ~longue & ~covid,
}
resume, tailles = {}, {}
for nom, masque in scenarios.items():
    n_lignes, n_mois, out = analyser(base[masque])
    resume[nom] = out
    tailles[nom] = f"{n_lignes} lignes / {n_mois} mois"

print("\nNombre de données par scénario :")
for nom, txt in tailles.items():
    print(f"  {nom} : {txt}")
print("\nEcart de taux de retard (points de %) entre mois plus extrêmes et plus calmes que la normale")
print(pd.DataFrame(resume).to_string())
print("\n|t| > 2 : écart probablement réel. |t| < 2 : indistinguable du hasard.")