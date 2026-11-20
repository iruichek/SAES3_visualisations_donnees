-- =====================================================================
-- 01_donnees_tgv_meteo.sql
-- Données du projet : régularité des TGV (SNCF) croisée avec la météo
-- mensuelle (Open-Meteo) par ville de départ.
--
-- Ordre d'exécution : ce fichier d'abord, puis 02_utilisateurs_accueil.sql
-- (tables utilisateurs, texte d'accueil, carrousel).
-- Le script peut être relancé sans danger (IF NOT EXISTS).
-- =====================================================================

CREATE DATABASE IF NOT EXISTS sae_tgv_meteo
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sae_tgv_meteo;

-- ---------------------------------------------------------------------
-- ville : une ligne par ville ayant une météo (47 villes)
-- Les coordonnées viennent de scripts/gares.py (valeurs approximatives).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ville (
                                     id         INT AUTO_INCREMENT PRIMARY KEY,
                                     nom        VARCHAR(60)   NOT NULL UNIQUE,
    latitude   DECIMAL(8,5)  NOT NULL,
    longitude  DECIMAL(8,5)  NOT NULL
    );

-- ---------------------------------------------------------------------
-- gare : une ligne par gare du jeu de données (59 gares)
-- ville_id vaut NULL pour les gares étrangères (Madrid, Zurich...) :
-- elles n'ont pas de météo associée.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gare (
                                    id        INT AUTO_INCREMENT PRIMARY KEY,
                                    nom       VARCHAR(60) NOT NULL UNIQUE,
    ville_id  INT NULL,
    CONSTRAINT fk_gare_ville FOREIGN KEY (ville_id) REFERENCES ville(id)
    );

-- ---------------------------------------------------------------------
-- tgv : une ligne par liaison (gare de départ -> gare d'arrivée) et par mois
-- Source : dataset SNCF « regularite-mensuelle-tgv-aqst », après nettoyage.
-- Les valeurs impossibles ou aberrantes sont à NULL (voir rapport qualité).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tgv (
                                   id                                    INT AUTO_INCREMENT PRIMARY KEY,
                                   mois                                  DATE NOT NULL,          -- 1er jour du mois
                                   service                               ENUM('NATIONAL','INTERNATIONAL') NOT NULL,
    gare_depart_id                        INT NOT NULL,
    gare_arrivee_id                       INT NOT NULL,
    duree_moyenne                         INT NULL,               -- minutes
    nb_train_prevu                        INT NOT NULL,
    nb_annulation                         INT NOT NULL,
    nb_train_depart_retard                INT NULL,
    retard_moyen_depart                   DOUBLE NULL,            -- minutes
    retard_moyen_tous_trains_depart       DOUBLE NULL,
    nb_train_retard_arrivee               INT NULL,
    retard_moyen_arrivee                  DOUBLE NULL,
    retard_moyen_tous_trains_arrivee      DOUBLE NULL,
    commentaires_retard_arrivee           TEXT NULL,
    nb_train_retard_sup_15                INT NULL,
    retard_moyen_trains_retard_sup15      DOUBLE NULL,            -- colonne déconseillée (incohérences source)
    nb_train_retard_sup_30                INT NULL,               -- colonne déconseillée (incohérences source)
    nb_train_retard_sup_60                INT NULL,
    prct_cause_externe                    DOUBLE NULL,
    prct_cause_infra                      DOUBLE NULL,
    prct_cause_gestion_trafic             DOUBLE NULL,
    prct_cause_materiel_roulant           DOUBLE NULL,
    prct_cause_gestion_gare               DOUBLE NULL,
    prct_cause_prise_en_charge_voyageurs  DOUBLE NULL,
    prevu_nul                             TINYINT(1) NOT NULL,    -- 1 = aucun train prévu ce mois-là
    UNIQUE KEY uq_tgv (mois, service, gare_depart_id, gare_arrivee_id),
    INDEX idx_tgv_depart_mois (gare_depart_id, mois),
    CONSTRAINT fk_tgv_depart  FOREIGN KEY (gare_depart_id)  REFERENCES gare(id),
    CONSTRAINT fk_tgv_arrivee FOREIGN KEY (gare_arrivee_id) REFERENCES gare(id)
    );

-- ---------------------------------------------------------------------
-- meteo_mensuelle : une ligne par ville et par mois (47 villes x 105 mois)
-- Agrégation mensuelle de la météo journalière.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS meteo_mensuelle (
                                               id                      INT AUTO_INCREMENT PRIMARY KEY,
                                               ville_id                INT NOT NULL,
                                               mois                    DATE NOT NULL,                        -- 1er jour du mois
                                               precip_cumul_mm         DOUBLE NULL,
                                               pluie_cumul_mm          DOUBLE NULL,
                                               temp_moy_c              DOUBLE NULL,
                                               rafale_max_kmh          DOUBLE NULL,
                                               nb_jours_gel            INT NULL,
                                               nb_jours_canicule       INT NULL,
                                               nb_jours_forte_pluie    INT NULL,
                                               nb_jours_vent_fort      INT NULL,
                                               nb_jours_neige          INT NULL,
                                               nb_jours_mesures        INT NULL,
                                               nb_jours_neige_marquee  INT NULL,
                                               mois_complet            TINYINT(1) NOT NULL,                  -- 1 = tous les jours du mois mesurés
    UNIQUE KEY uq_meteo (ville_id, mois),
    CONSTRAINT fk_meteo_ville FOREIGN KEY (ville_id) REFERENCES ville(id)
    );

-- ---------------------------------------------------------------------
-- v_tgv_meteo : le croisement TGV x météo
-- Une ligne TGV avec la météo du mois dans la ville de la gare de départ.
-- LEFT JOIN : les 775 lignes dont la gare de départ est étrangère sont
-- conservées, avec des colonnes météo à NULL.
-- taux_retard = trains en retard à l'arrivée / trains prévus
-- (NULL si aucun train prévu).
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_tgv_meteo AS
SELECT
    t.id,
    t.mois,
    t.service,
    gd.nom  AS gare_depart,
    ga.nom  AS gare_arrivee,
    v.nom   AS ville_depart,
    t.duree_moyenne,
    t.nb_train_prevu,
    t.nb_annulation,
    t.nb_train_retard_arrivee,
    t.retard_moyen_arrivee,
    t.retard_moyen_tous_trains_arrivee,
    t.nb_train_retard_sup_15,
    t.nb_train_retard_sup_60,
    t.prevu_nul,
    t.nb_train_retard_arrivee / NULLIF(t.nb_train_prevu, 0)  AS taux_retard,
    t.nb_annulation           / NULLIF(t.nb_train_prevu, 0)  AS taux_annulation,
    m.precip_cumul_mm,
    m.pluie_cumul_mm,
    m.temp_moy_c,
    m.rafale_max_kmh,
    m.nb_jours_gel,
    m.nb_jours_canicule,
    m.nb_jours_forte_pluie,
    m.nb_jours_vent_fort,
    m.nb_jours_neige,
    m.mois_complet
FROM tgv t
         JOIN gare gd              ON gd.id = t.gare_depart_id
         JOIN gare ga              ON ga.id = t.gare_arrivee_id
         LEFT JOIN ville v         ON v.id = gd.ville_id
         LEFT JOIN meteo_mensuelle m ON m.ville_id = gd.ville_id AND m.mois = t.mois;