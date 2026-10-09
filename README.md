# Météo et retards des trains en France

Projet de SAE, Groupe 7 (sujet type 2).

Site web qui permet d'étudier l'influence des conditions météorologiques (température, précipitations, neige, vent) sur la ponctualité des TER en France. Il croise les données de régularité mensuelle des TER (SNCF Open Data) avec les données météo historiques par région (Open-Meteo, données Météo-France).

> Les éléments entre `[crochets]` sont à compléter par l'équipe.

---

## Sommaire

1. [Fonctionnalités](#fonctionnalités)
2. [Technologies](#technologies)
3. [Structure du dépôt](#structure-du-dépôt)
4. [Prérequis](#prérequis)
5. [Installation et lancement](#installation-et-lancement)
6. [Comptes de test](#comptes-de-test)
7. [Documentation de l'API (Swagger)](#documentation-de-lapi-swagger)
8. [Sources de données](#sources-de-données)
9. [Limites et remarques](#limites-et-remarques)
10. [Équipe](#équipe)

---

## Fonctionnalités

### Visiteur (non connecté)
- Lire le texte de présentation du service
- Parcourir le carrousel de 3 graphiques générés côté serveur (régularité par région, courbe régularité / précipitations, nuage de points régularité / météo)
- Accéder à la connexion et à l'inscription

### Utilisateur enregistré
- Page d'**analyse descriptive** : moyenne, médiane, mode, écart-type, minimum, maximum et histogramme sur un indicateur au choix
- Page **Évolution de la ponctualité et de la météo** : courbe à deux axes pour une région et une période
- Page **Météo et retards** : nuage de points avec droite de régression et coefficient de corrélation
- Page **Événements météo extrêmes** *(S4)*
- Page **Classement des régions** *(S4)*
- Page de profil : changer son login et son mot de passe *(S4)*

### Administrateur
- Gérer les utilisateurs (lister, supprimer, modifier)
- Modifier le texte d'accueil et les images du carrousel
- Relancer la génération des graphiques d'accueil *(S4)*

---

## Technologies

| Couche | Technologie |
|---|---|
| Collecte et nettoyage des données | Python, pandas |
| Base de données | MySQL |
| API | Node.js, Express |
| Documentation de l'API | OpenAPI / Swagger |
| Front-end | Vue 3, Vue Router, Pinia |
| Graphiques d'accueil | Python ([matplotlib ou plotly]) |
| Graphiques dynamiques | [bibliothèque à préciser] |
| Sécurité | bcrypt, [JWT ou session] |

Chaîne de données :
`API externes → scripts Python → JSON bruts → nettoyage → CSV propres → MySQL → API Express → Vue.js`

---

## Structure du dépôt

```
.
├── front/          Application Vue.js
├── api/            API Node.js + Express (sert aussi les fichiers statiques)
├── scripts/        Scripts Python : collecte, nettoyage, graphiques, chargement en base
├── sql/            Scripts SQL (create_db.sql)
├── docs/           Cadrage, spécifications, notes d'exploration des API, rapport de qualité
├── data/
│   ├── raw/        Données brutes (JSON issus des API)
│   └── clean/      Données nettoyées (prêtes à charger en base)
└── README.md
```

---

## Prérequis

- [Node.js](https://nodejs.org/) version [à préciser]
- [Python](https://www.python.org/) version [à préciser] et `pip`
- [MySQL](https://www.mysql.com/) version [à préciser]
- Git

---

## Installation et lancement

### 1. Récupérer le projet

```bash
git clone [URL du dépôt]
cd [nom du dossier]
```

### 2. Installer les dépendances Python

```bash
cd scripts
pip install -r requirements.txt
cd ..
```

### 3. Créer la base de données

```bash
mysql -u [utilisateur] -p < sql/create_db.sql
```

### 4. Configurer l'API

Créer un fichier `.env` dans le dossier `api/` (ne jamais le publier sur GitHub) :

```
DB_HOST=[hôte]
DB_PORT=[port]
DB_USER=[utilisateur]
DB_PASSWORD=[mot de passe]
DB_NAME=[nom de la base]
PORT=[port de l'API]
```

### 5. Récupérer, nettoyer et charger les données

Les données nettoyées sont déjà fournies dans `data/clean/` : [oui / non, à préciser]. Pour les régénérer :

```bash
cd scripts
python collect_sncf.py       # collecte SNCF  -> data/raw/
python collect_meteo.py      # collecte météo -> data/raw/
python [script de nettoyage] # nettoyage      -> data/clean/
python load_db.py            # chargement dans MySQL
cd ..
```

### 6. Générer les graphiques de la page d'accueil

```bash
cd scripts
python [script des graphiques]
cd ..
```

### 7. Lancer l'API

```bash
cd api
npm install
npm start
```

L'API est disponible sur `http://localhost:[port]`.

### 8. Lancer le front

**Mode développement :**

```bash
cd front
npm install
npm run dev
```

Le site est disponible sur `http://localhost:[port]`.

**Mode production :** le front compilé (`npm run build`) est servi par l'API à l'adresse `http://localhost:[port de l'API]`.

> Pour la phase S3, le front peut fonctionner **sans l'API**, avec une source de données locale (extraits JSON). [À préciser : comment activer ce mode.]

---

## Comptes de test

| Rôle | Login | Mot de passe |
|---|---|---|
| Administrateur | `[login]` | `[mot de passe]` |
| Utilisateur | `[login]` | `[mot de passe]` |

Ces comptes sont créés lors du chargement de la base. Les mots de passe sont stockés hachés (bcrypt).

---

## Documentation de l'API (Swagger)

Une fois l'API lancée, la documentation interactive est disponible à l'adresse :

`http://localhost:[port]/[chemin de Swagger]`

Elle permet de tester toutes les routes sans passer par le front. Les routes sont regroupées par famille : authentification, accueil, référentiels, données, graphiques, profil, administration.

---

## Sources de données

| Source | Contenu | Lien |
|---|---|---|
| SNCF Open Data | Régularité mensuelle des TER | https://data.sncf.com/explore/dataset/regularite-mensuelle-ter/ |
| Open-Meteo (historique) | Météo journalière par région (données Météo-France) | https://open-meteo.com/ |

Les données météo sont récupérées pour un point représentatif de chaque région (le chef-lieu), puis agrégées au mois pour correspondre à la granularité des données SNCF.

Open-Meteo est utilisé dans le cadre de son offre gratuite non commerciale. Ses limites d'appels sont à respecter (voir les conditions d'utilisation sur leur site).

---

## Limites et remarques

- Les résultats montrent des **corrélations**, pas des causes : un retard peut aussi venir de travaux, de grèves ou d'incidents techniques.
- Une seule station météo (le chef-lieu) représente chaque région, ce qui limite la précision.
- [Autres limites rencontrées : données manquantes, régions fusionnées, etc.]

---

## Équipe

Groupe 7 :

- [Prénom Nom] : [rôle]
- [Prénom Nom] : [rôle]
- [Prénom Nom] : [rôle]
- [Prénom Nom] : [rôle]

Projet réalisé dans le cadre de la SAE, [formation / établissement], [année].
