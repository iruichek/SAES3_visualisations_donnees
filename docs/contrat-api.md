# Contrat d'API — Lot 4 : analyses et données de graphiques

*Étudiant 4 — à valider avec l'équipe avant de coder (voir « Points à valider » en fin de document).*

Les exemples de réponse ci-dessous ont été **calculés sur les fichiers réels** `data/clean/tgv_clean.csv`, `meteo_mois.csv` et `meteo_jour.csv` du dépôt. Pour les listes longues, seul un extrait est montré.

## 1. Règles communes

| Règle | Détail |
|---|---|
| Préfixe | toutes les routes commencent par `/api` |
| Session | paramètre `session` **obligatoire** (phase S3), fourni par la connexion (lot 3). Remplacé plus tard par un jeton dans l'en-tête `Authorization` (S4) |
| Format | réponses en JSON, UTF-8 |
| Dates | `YYYY-MM` ou `YYYY-MM-DD`. `debut=2023-01` signifie le 1er janvier, `fin=2023-12` signifie le 31 décembre. Toutes les dates en filtre sont facultatives |
| Ville | nom exact tel que renvoyé par `GET /api/villes` (accents et espaces encodés dans l'URL) |
| Lignes exclues | les 775 lignes TGV sans ville de départ (gares étrangères) sont exclues de toutes les routes |
| Résultat vide | un filtre valide sans donnée répond **200** avec `total: 0` et une liste vide (jamais une erreur) |

**Définition du taux de retard** (à valider) : `taux_retard = nb_train_retard_arrivee / nb_train_prevu`, entre 0 et 1. Les lignes où `nb_train_prevu = 0` (73 lignes) sont exclues du calcul. Quand on regroupe plusieurs liaisons (routes `evolution` et `correlation`), le taux est `somme des retards / somme des trains prévus`, jamais la moyenne des taux.

**Format d'erreur** (comme dans le cours) :

```json
{
  "erreur": {
    "code": "CHAMP_INVALIDE",
    "message": "Le champ « foo » n'existe pas dans la source tgv."
  }
}
```

## 2. Tableau des routes

| US | Méthode et chemin | Query | Corps | Succès | Erreurs |
|---|---|---|---|---|---|
| US-32 | `GET /api/villes` | | | 200 | 401 |
| US-31 | `GET /api/sources` | | | 200 | 401 |
| US-32, US-34 | `GET /api/sources/:source/enregistrements` | `champ`*, `ville`, `debut`, `fin`, `page`, `limite` | | 200 | 400, 401, 404 |
| US-33 | `GET /api/sources/:source/statistiques` | `champ`*, `ville`, `debut`, `fin` | | 200 | 400, 401, 404 |
| US-36 | `GET /api/villes/:ville/evolution` | `variable_meteo`*, `debut`, `fin` | | 200 | 400, 401, 404 |
| US-37 | `GET /api/analyses/correlation` | `variable_meteo`*, `ville`, `saison`, `annee_debut`, `annee_fin` | | 200 | 400, 401 |

`*` = obligatoire. Toutes les routes sont en `GET` : aucune ne modifie les données, donc pas de corps.

**Pourquoi la ville est dans le chemin pour `evolution` mais en query ailleurs** (règle du cours) : pour la courbe d'évolution, sans la ville on ne sait pas de quoi on parle, donc elle désigne la ressource (et une ville inconnue donne 404). Pour les autres routes, la ville est un filtre facultatif (et une ville inconnue donne 400).

### Codes d'erreur

| HTTP | Code | Quand |
|---|---|---|
| 400 | `CHAMP_INVALIDE` | `champ` absent, ou absent de la liste de la source |
| 400 | `VARIABLE_METEO_INVALIDE` | `variable_meteo` absente ou hors liste (voir §4) |
| 400 | `VILLE_INCONNUE` | `ville` en query absente de `/api/villes` |
| 400 | `PERIODE_INVALIDE` | date mal formée, ou `debut` après `fin` |
| 400 | `SAISON_INVALIDE` | `saison` autre que `hiver`, `printemps`, `ete`, `automne` |
| 400 | `PAGINATION_INVALIDE` | `page` ou `limite` non numérique, ou hors bornes |
| 401 | `NON_AUTHENTIFIE` | paramètre `session` manquant |
| 404 | `SOURCE_INCONNUE` | `:source` n'est pas `tgv`, `meteo_mois` ou `meteo_jour` |
| 404 | `VILLE_INCONNUE` | `:ville` du chemin absente de `/api/villes` |
| 500 | `ERREUR_INTERNE` | erreur serveur ou base inaccessible |

## 3. Détail des routes

### GET /api/villes — US-32

Liste des villes pour remplir le filtre.

```
GET /api/villes?session=abc123
```

Réponse 200 (extrait, 47 villes au total) :

```json
{
  "total": 47,
  "villes": [
    {
      "nom": "Aix-en-Provence"
    },
    {
      "nom": "Angers"
    },
    {
      "nom": "Angoulême"
    }
  ]
}
```

### GET /api/sources — US-31

Les sources disponibles et leurs champs numériques, pour remplir les listes « table » et « champ ».

```
GET /api/sources?session=abc123
```

Réponse 200 (liste de champs abrégée par « … ») :

```json
{
  "total": 3,
  "sources": [
    {
      "id": "tgv",
      "periode": {
        "debut": "2018-01",
        "fin": "2026-09"
      },
      "champs": [
        "duree_moyenne",
        "nb_train_prevu",
        "nb_annulation",
        "…",
        "taux_retard"
      ]
    },
    {
      "id": "meteo_mois",
      "periode": {
        "debut": "2018-01",
        "fin": "2026-09"
      },
      "champs": [
        "precip_cumul_mm",
        "temp_moy_c",
        "rafale_max_kmh",
        "…"
      ]
    },
    {
      "id": "meteo_jour",
      "periode": {
        "debut": "2018-01-01",
        "fin": "2026-09-30"
      },
      "champs": [
        "temp_max_c",
        "temp_min_c",
        "precip_mm",
        "…"
      ]
    }
  ]
}
```

Liste complète des champs :

- `tgv` : `duree_moyenne`, `nb_train_prevu`, `nb_annulation`, `nb_train_depart_retard`, `retard_moyen_depart`, `retard_moyen_tous_trains_depart`, `nb_train_retard_arrivee`, `retard_moyen_arrivee`, `retard_moyen_tous_trains_arrivee`, `nb_train_retard_sup_15`, `retard_moyen_trains_retard_sup15`, `nb_train_retard_sup_30`, `nb_train_retard_sup_60`, `prct_cause_externe`, `prct_cause_infra`, `prct_cause_gestion_trafic`, `prct_cause_materiel_roulant`, `prct_cause_gestion_gare`, `prct_cause_prise_en_charge_voyageurs`, `taux_retard`, `taux_retard`
- `meteo_mois` : `precip_cumul_mm`, `pluie_cumul_mm`, `temp_moy_c`, `rafale_max_kmh`, `nb_jours_gel`, `nb_jours_canicule`, `nb_jours_forte_pluie`, `nb_jours_vent_fort`, `nb_jours_neige`, `nb_jours_neige_marquee`
- `meteo_jour` : `temp_max_c`, `temp_min_c`, `temp_moy_c`, `precip_mm`, `pluie_mm`, `neige_cm`, `vent_max_kmh`, `rafale_max_kmh`

`taux_retard` est un champ calculé (voir §1). Les colonnes `annee`, `mois_complet`, `nb_jours_mesures` et `code_meteo` ne sont pas proposées (peu utiles en statistiques).

### GET /api/sources/:source/enregistrements — US-32, US-34

Les valeurs d'un champ, filtrées par ville et période. Elles servent au tableau et à l'histogramme. Tri fixe : date croissante. `page` vaut 1 par défaut, `limite` vaut 1000 par défaut (maximum 20 000).

Champ `contexte` : pour `tgv`, la liaison (`gare_depart → gare_arrivee (service)`) ; pour les sources météo, `null`.

```
GET /api/sources/tgv/enregistrements?champ=taux_retard&ville=Lyon&debut=2023-01&fin=2023-12&limite=3&session=abc123
```

Réponse 200 :

```json
{
  "source": "tgv",
  "champ": "taux_retard",
  "ville": "Lyon",
  "debut": "2023-01",
  "fin": "2023-12",
  "total": 72,
  "page": 1,
  "limite": 3,
  "pages": 24,
  "enregistrements": [
    {
      "ville": "Lyon",
      "date": "2023-01-01",
      "valeur": 0.2433,
      "contexte": "LYON PART DIEU → LILLE (NATIONAL)"
    },
    {
      "ville": "Lyon",
      "date": "2023-01-01",
      "valeur": 0.2236,
      "contexte": "LYON PART DIEU → MARNE LA VALLEE (NATIONAL)"
    },
    {
      "ville": "Lyon",
      "date": "2023-01-01",
      "valeur": 0.1721,
      "contexte": "LYON PART DIEU → MARSEILLE ST CHARLES (NATIONAL)"
    }
  ]
}
```

Réponse 400 (champ inexistant) :

```json
{
  "erreur": {
    "code": "CHAMP_INVALIDE",
    "message": "Le champ « foo » n'existe pas dans la source tgv."
  }
}
```

### GET /api/sources/:source/statistiques — US-33

Statistiques calculées par le serveur sur les mêmes lignes que `enregistrements`. Elles servent de **valeurs de référence** pour vérifier le calcul fait en JavaScript par le front.

```
GET /api/sources/tgv/statistiques?champ=taux_retard&ville=Lyon&debut=2023-01&fin=2023-12&session=abc123
```

Réponse 200 :

```json
{
  "source": "tgv",
  "champ": "taux_retard",
  "ville": "Lyon",
  "debut": "2023-01",
  "fin": "2023-12",
  "statistiques": {
    "effectif": 72,
    "moyenne": 0.1787,
    "mediane": 0.1874,
    "mode": null,
    "ecart_type": 0.0794,
    "min": 0.0333,
    "max": 0.3646
  }
}
```

Règles : les valeurs nulles sont ignorées ; `ecart_type` est l'écart-type **d'échantillon** (division par n−1) ; `mode` est un tableau (plusieurs valeurs possibles) ou `null` quand aucune valeur ne se répète. Sans donnée, `effectif` vaut 0 et toutes les autres statistiques valent `null`.

### GET /api/villes/:ville/evolution — US-36

Série mensuelle de la ville : retards, annulations et une variable météo, pour la courbe à deux axes. Triée par mois croissant. Un mois sans donnée TGV ou sans météo n'apparaît pas.

```
GET /api/villes/Lyon/evolution?variable_meteo=precip_cumul_mm&debut=2023-01&fin=2023-06&session=abc123
```

Réponse 200 :

```json
{
  "ville": "Lyon",
  "variable_meteo": "precip_cumul_mm",
  "debut": "2023-01",
  "fin": "2023-06",
  "total": 6,
  "serie": [
    {
      "mois": "2023-01",
      "taux_retard": 0.1499,
      "nb_train_prevu": 2115,
      "nb_train_retard_arrivee": 317,
      "nb_annulation": 103,
      "meteo": {
        "variable": "precip_cumul_mm",
        "valeur": 53.2
      }
    },
    {
      "mois": "2023-02",
      "taux_retard": 0.1588,
      "nb_train_prevu": 1876,
      "nb_train_retard_arrivee": 298,
      "nb_annulation": 79,
      "meteo": {
        "variable": "precip_cumul_mm",
        "valeur": 6.0
      }
    },
    {
      "mois": "2023-03",
      "taux_retard": 0.1304,
      "nb_train_prevu": 2186,
      "nb_train_retard_arrivee": 285,
      "nb_annulation": 663,
      "meteo": {
        "variable": "precip_cumul_mm",
        "valeur": 104.9
      }
    },
    {
      "mois": "2023-04",
      "taux_retard": 0.1871,
      "nb_train_prevu": 2100,
      "nb_train_retard_arrivee": 393,
      "nb_annulation": 75,
      "meteo": {
        "variable": "precip_cumul_mm",
        "valeur": 72.3
      }
    },
    {
      "mois": "2023-05",
      "taux_retard": 0.167,
      "nb_train_prevu": 2198,
      "nb_train_retard_arrivee": 367,
      "nb_annulation": 31,
      "meteo": {
        "variable": "precip_cumul_mm",
        "valeur": 94.3
      }
    },
    {
      "mois": "2023-06",
      "taux_retard": 0.2146,
      "nb_train_prevu": 2144,
      "nb_train_retard_arrivee": 460,
      "nb_annulation": 16,
      "meteo": {
        "variable": "precip_cumul_mm",
        "valeur": 86.6
      }
    }
  ]
}
```

Réponse 404 :

```json
{
  "erreur": {
    "code": "VILLE_INCONNUE",
    "message": "La ville « Lyonn » n'existe pas."
  }
}
```

### GET /api/analyses/correlation — US-37

Un point par ville et par mois : la variable météo choisie et le taux de retard. Le front calcule la droite de régression et le coefficient de corrélation. Tri : mois croissant puis ville.

```
GET /api/analyses/correlation?variable_meteo=nb_jours_vent_fort&saison=hiver&annee_debut=2023&annee_fin=2024&session=abc123
```

Réponse 200 (extrait : 282 points au total, 3 montrés) :

```json
{
  "variable_meteo": "nb_jours_vent_fort",
  "saison": "hiver",
  "annee_debut": 2023,
  "annee_fin": 2024,
  "ville": null,
  "total": 282,
  "points": [
    {
      "ville": "Aix-en-Provence",
      "mois": "2023-01",
      "valeur_meteo": 1,
      "taux_retard": 0.0924,
      "nb_train_prevu": 433
    },
    {
      "ville": "Angers",
      "mois": "2023-01",
      "valeur_meteo": 0,
      "taux_retard": 0.1016,
      "nb_train_prevu": 551
    },
    {
      "ville": "Angoulême",
      "mois": "2023-01",
      "valeur_meteo": 0,
      "taux_retard": 0.1108,
      "nb_train_prevu": 334
    }
  ]
}
```

`ville` vaut `null` quand le filtre n'est pas utilisé (toutes les villes).

## 4. Valeurs autorisées

- **`variable_meteo`** : `temp_moy_c`, `precip_cumul_mm`, `rafale_max_kmh`, `nb_jours_gel`, `nb_jours_canicule`, `nb_jours_forte_pluie`, `nb_jours_vent_fort`, `nb_jours_neige` (colonnes de `meteo_mois.csv`).
- **`saison`** : `hiver` (décembre, janvier, février), `printemps` (mars à mai), `ete` (juin à août), `automne` (septembre à novembre). Les filtres `annee_debut` et `annee_fin` portent sur l'année civile du mois (décembre 2023 compte pour 2023).
- **Données** : la jointure TGV et météo se fait sur `ville_depart` (TGV) et `ville` (météo) + le mois. Elle couvre 12 132 lignes TGV sur 12 907.

## 5. Rangement du code (RCSM)

| Routeur | Routes | Besoin métier |
|---|---|---|
| `referentiels` | `/villes`, `/sources` | choisir quoi analyser |
| `analyses` | `/sources/:source/enregistrements`, `/sources/:source/statistiques`, `/villes/:ville/evolution`, `/analyses/correlation` | explorer les données |

Chaque routeur a son contrôleur (conversion et validation des paramètres, qui arrivent en texte) et son service (requêtes SQL préparées, avec une liste blanche des sources, champs et variables : les noms de colonnes ne peuvent pas passer en paramètre préparé).

## 6. Points à valider avec l'équipe

1. **Définition du `taux_retard`** (§1) avec les étudiants 1 et 2.
2. **Écart-type** : échantillon (n−1) ici. Le front doit utiliser la même formule, sinon ses valeurs ne coïncideront pas avec la référence.
3. **Noms des sources** (`tgv`, `meteo_mois`, `meteo_jour`) : à aligner sur les tables du schéma MySQL (étudiant 2).
4. **Pagination et calcul en JS** : le front doit recevoir toutes les valeurs pour son histogramme. `limite` peut aller jusqu'à 20 000 : `tgv` entier (12 907 lignes) tient en un appel, mais `meteo_jour` entier (150 165 lignes) demande plusieurs pages, ou un filtre par ville.
5. **Ville dans le chemin** pour `evolution` (§2) : à confirmer avec l'étudiant 5 pour ses services.
6. **Paramètre `session`** : confirmer avec l'étudiant 3 le nom et la façon dont il est transmis.
7. **Hors contrat pour l'instant (Could)** : indice base 100 sur l'évolution, coefficient de corrélation calculé côté serveur.
