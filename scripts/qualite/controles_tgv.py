import sys
import pandas as pd

df = pd.read_csv("data/clean/tgv_clean.csv", sep=";")
erreurs, alertes = 0, 0


def controle(nom, ok, bloquant=True, detail=""):
    global erreurs, alertes
    if ok:
        print(f"  OK       {nom}")
    elif bloquant:
        erreurs += 1
        print(f"  ERREUR   {nom} {detail}")
    else:
        alertes += 1
        print(f"  ALERTE   {nom} {detail}")


print("EXHAUSTIVITE")
requises = ["date", "service", "gare_depart", "gare_arrivee",
            "nb_train_prevu", "nb_annulation", "nb_train_retard_arrivee"]
for col in requises:
    controle(f"{col} : aucune valeur manquante", df[col].notna().all(),
             detail=f"({df[col].isna().sum()} manquantes)")
controle("au moins 1000 lignes", len(df) >= 1000, detail=f"({len(df)} lignes)")
controle("période 2018-01 à 2026-09 couverte",
         df["date"].min() == "2018-01" and df["date"].max() == "2026-09",
         detail=f"({df['date'].min()} -> {df['date'].max()})")
mois = df["date"].nunique()
controle("aucun mois manquant dans la période (105 mois)", mois == 105,
         bloquant=False, detail=f"({mois} mois présents)")

print("\nCOHERENCE")
cle = ["date", "service", "gare_depart", "gare_arrivee"]
controle("aucun doublon", df.duplicated(subset=cle).sum() == 0)
for col in ["nb_train_prevu", "nb_annulation", "nb_train_retard_arrivee",
            "nb_train_retard_sup_15", "nb_train_retard_sup_30",
            "nb_train_retard_sup_60"]:
    controle(f"{col} : aucune valeur négative", (df[col].dropna() < 0).sum() == 0)
controle("retards <= trains prévus (hors lignes sans train prévu)",
         (df[~df["prevu_nul"]]["nb_train_retard_arrivee"]
          > df[~df["prevu_nul"]]["nb_train_prevu"]).sum() == 0)
hors = df[(df["nb_annulation"] > df["nb_train_prevu"]) & ~df["prevu_nul"]]
controle("annulations <= prévus (hors lignes sans train prévu)", len(hors) == 0,
         detail=f"({len(hors)} lignes)")
ok = (df["nb_train_retard_sup_15"].notna() & df["nb_train_retard_sup_30"].notna()
      & df["nb_train_retard_sup_60"].notna())
v60_30 = (ok & (df["nb_train_retard_sup_60"] > df["nb_train_retard_sup_30"])).sum()
v30_15 = (ok & (df["nb_train_retard_sup_30"] > df["nb_train_retard_sup_15"])).sum()

causes = [c for c in df.columns if c.startswith("prct_cause_")]
somme = df[causes].sum(axis=1)
controle("somme des causes proche de 100 % (99,5 à 100,5)",
         somme.between(99.5, 100.5).mean() > 0.95, bloquant=False,
         detail=f"({somme.between(99.5, 100.5).mean():.1%} des lignes)")
controle("retards >60 <= retards >30 (hors NULL)", v60_30 == 0,
         bloquant=False, detail=f"({v60_30} lignes, {v60_30 / ok.sum():.1%})")
controle("retards >30 <= retards >15 (hors NULL)", v30_15 == 0,
         bloquant=False, detail=f"({v30_15} lignes)")
controle("service = National ou International",
         df["service"].isin(["NATIONAL", "INTERNATIONAL"]).all())
controle("durée moyenne entre 20 et 900 min (hors NULL)",
         df["duree_moyenne"].dropna().between(20, 900).all(), bloquant=False)

print(f"\nRésultat : {erreurs} erreur(s), {alertes} alerte(s)")
sys.exit(1 if erreurs else 0)