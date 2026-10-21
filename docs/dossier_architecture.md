# Dossier d'architecture — Plateforme Data Omnicanale NeoRetail

| | |
|---|---|
| **Version** | Jalon S0 — document mis à jour à chaque jalon (S0 → S8) |
| **Statut** | Validé en cadrage |
| **Périmètre** | Lakehouse Bronze / Silver / Gold, batch + streaming, qualité, ML, BI, observabilité |
| **Date** | 21/10/2026 |
| **Format livré** | `docs/L1_dossier_architecture.pdf` (généré par `scripts/generer_documentation.py`) |

---

## 1. Contexte et objectifs

NeoRetail est une enseigne omnicanale (e-commerce web et mobile, marketplace, 200 magasins physiques).
Les décisions opérationnelles (stocks, prix, promotions) reposent aujourd'hui sur des sources
cloisonnées. La plateforme vise à fournir **une vision unifiée et fiable des ventes, du parcours
client et des retours**, ainsi qu'une **prévision de la demande** exploitable par les équipes métier.

| Objectif pédagogique | Réponse de l'architecture |
|---|---|
| O1 — Architecture cloud-agnostic | Stockage objet S3 (MinIO), format ouvert Iceberg, moteurs interchangeables (§3, §4) |
| O2 — Pipelines batch et streaming | Airflow (batch idempotent), Redpanda + Spark Structured Streaming (§6) |
| O3 — Qualité et gouvernance | Great Expectations, contrats de données YAML, traçabilité OpenLineage, RGPD (§9, §10) |
| O4 — Modélisation | dbt : `stg_` → `int_` → `dim_` / `fct_`, schéma en étoile + couche sémantique (§7) |
| O5 — Cas d'usage ML | Prévision de la demande journalière, MLflow, prévision quotidienne en batch (§6.4) |
| O6 — Automatisation et exploitation | Docker Compose, GitHub Actions, Makefile, Prometheus / Grafana (§11, §12) |

### KPIs métier retenus pour la BI (L6)

1. **Chiffre d'affaires** net par canal et par période
2. **Panier moyen** (CA / nombre de commandes ou tickets)
3. **Taux de conversion** web (sessions avec achat / sessions)
4. **Taux de retour** (montant retourné / CA)
5. **Prévision vs réalisé** (erreur MAPE, cible < 15 %)

> Le KPI « rupture de stock » cité en exemple dans le sujet n'est pas réalisable : le pack de
> données ne contient aucune donnée d'inventaire. Ce point est tracé dans les risques et perspectives (§13).

---

## 2. Sources de données

Pack synthétique fourni (`neoretail_bigdata_pack`), période **01/01/2025 → 31/08/2026**,
**3,37 M lignes / événements**. Profilage détaillé : [profilage_donnees.md](profilage_donnees.md) ; description de chaque colonne : [dictionnaire_donnees.md](dictionnaire_donnees.md).

| Source | Format | Volume | Mode d'ingestion | Rôle |
|---|---|---|---|---|
| `pos_sales` | CSV gz | 500 000 | Batch quotidien | Ventes magasins (ligne de ticket) |
| `orders` | CSV gz | 500 000 | Batch quotidien | En-têtes de commandes en ligne |
| `order_items` | CSV gz | 1 000 000 | Batch quotidien | Lignes de commandes en ligne |
| `returns` | CSV gz | 100 000 | Batch quotidien | Retours logistiques |
| `customers` | CSV gz | 100 000 | Batch (référentiel) | Référentiel clients (état initial) |
| `customer_updates` | JSONL gz | 50 000 | Batch (CDC) | Changements clients (U / D) → SCD2 |
| `products` | CSV gz | 20 000 | Batch (référentiel) | Catalogue produits |
| `stores` | CSV gz | 200 | Batch (référentiel) | Référentiel magasins |
| `clickstream` | JSONL gz | 1 000 000 | **Streaming** (Redpanda) | Événements web / mobile |
| `gl_entries` | CSV gz | 100 000 | Batch (optionnel) | Écritures ERP — hors périmètre de la première version |

**Simulation du quotidien.** Les fichiers sont livrés « en bloc ». Un script de découpage
(S1) les redistribue dans la zone d'atterrissage par date métier
(`landing/<source>/dt=YYYY-MM-DD/`). Le DAG Airflow est ainsi exécuté **par jour** et démontre
le rattrapage d'historique (backfill), la reprise sur erreur et l'idempotence (rejouer = même résultat). Les référentiels sont chargés en totalité à chaque exécution (faible volume).

---

## 3. Architecture logique

@@SCHEMA:01_architecture_logique@@

*Schéma : `docs/diagrammes/01_architecture_logique.pdf`.*


### Principes directeurs

- **Séparation stockage / calcul** : les données vivent dans MinIO au format ouvert Iceberg ;
  Trino et Spark ne sont que des moteurs. Migration vers S3, GCS ou ADLS sans réécriture.
- **ELT** : chargement brut en Bronze, transformations en SQL versionné (dbt) dans le lakehouse.
- **Idempotence partout** : chaque écriture est rejouable sans doublon (remplacement de partition
  en batch, point de reprise + clé d'événement en streaming, fusion `merge` en dbt).
- **Qualité au plus tôt** : contrôles à chaque passage de zone, données non conformes en
  quarantaine plutôt que supprimées.
- **Protection des données dès la conception** : les identifiants personnels ne quittent jamais Bronze en clair.

---

## 4. Architecture physique

Déploiement local mono-hôte via **Docker Compose** (cible : 16 Go RAM, 4 vCPU). Chaque service
correspond à un service managé équivalent dans le cloud (colonne de droite) : c'est ce qui
garantit le caractère cloud-agnostic.

@@SCHEMA:02_architecture_physique@@

*Schéma : `docs/diagrammes/02_architecture_physique.pdf`.*

| Service | Image (indicative) | Port | RAM | Rôle | Équivalent cloud |
|---|---|---|---|---|---|
| `minio` | minio/minio | 9000 / 9001 | 0,5 Go | Stockage objet (landing, lakehouse, artefacts) | S3 / GCS / ADLS |
| `postgres` | postgres:16 | 5432 | 0,5 Go | Backends : metastore, Airflow, Superset, MLflow, Marquez | RDS / Cloud SQL |
| `hive-metastore` | apache/hive:4 | 9083 | 0,5 Go | Catalogue technique Iceberg | Glue Catalog |
| `trino` | trinodb/trino | 8080 | 3 Go | Moteur SQL (dbt, GE, Superset) | Athena / Starburst |
| `redpanda` | redpandadata/redpanda | 9092 | 1 Go | File de messages compatible Kafka | MSK / Confluent |
| `redpanda-console` | redpandadata/console | 8085 | 0,2 Go | Interface : topics, retard du consommateur | — |
| `spark-streaming` | bitnami/spark (+ bibliothèques Iceberg) | 4040 | 2 Go | Consommateur clickstream → Bronze | EMR / Dataproc |
| `airflow` (webserver + scheduler) | apache/airflow | 8081 | 2 Go | Orchestration (LocalExecutor) | MWAA / Composer |
| `mlflow` | ghcr.io/mlflow/mlflow | 5000 | 0,5 Go | Suivi des expériences + registre de modèles | SageMaker / Vertex |
| `superset` | apache/superset | 8088 | 1 Go | BI | QuickSight / Looker |
| `marquez` (+ web) | marquezproject/marquez | 5002 / 3000 | 0,7 Go | Traçabilité (OpenLineage) | Purview / Dataplex |
| `prometheus` | prom/prometheus | 9090 | 0,3 Go | Métriques | CloudWatch / Managed Prometheus |
| `pushgateway` | prom/pushgateway | 9091 | 0,1 Go | Métriques des traitements batch | — |
| `statsd-exporter` | prom/statsd-exporter | 9102 | 0,1 Go | Métriques Airflow | — |
| `alertmanager` | prom/alertmanager | 9093 | 0,1 Go | Alertes (webhook simulé) | SNS / PagerDuty |
| `grafana` | grafana/grafana | 3001 | 0,3 Go | Tableaux de bord SLO | Managed Grafana |
| `datadocs` | nginx:alpine | 8082 | 0,05 Go | Publication des rapports qualité GE + documentation dbt | Site statique S3 |

**Total estimé : ~13 Go.** Mode allégé possible (`make up-lite`) : sans Marquez ni Superset
pendant le développement.

### Organisation du stockage (MinIO)

```
s3://landing/<source>/dt=YYYY-MM-DD/<fichier>     # dépôt brut des fichiers sources
s3://lakehouse/warehouse/bronze.db/...            # tables Iceberg Bronze
s3://lakehouse/warehouse/silver.db/...            # tables Iceberg Silver
s3://lakehouse/warehouse/gold.db/...              # tables Iceberg Gold
s3://lakehouse/_checkpoints/clickstream/          # checkpoints Spark Streaming
s3://mlflow/                                      # artefacts MLflow (modèles, graphiques)
s3://datadocs/                                    # rapports qualité GE + documentation dbt (site statique)
```

---

## 5. Zones du lakehouse

| | **Bronze** | **Silver** | **Gold** |
|---|---|---|---|
| **Contenu** | Copie fidèle des sources | Données nettoyées, typées, conformes | Modèle analytique (étoile), agrégats (marts), prévisions |
| **Écriture** | Airflow (batch) / Spark (streaming) | dbt (`stg_`, `int_`) | dbt (`dim_`, `fct_`, `mart_`), traitement ML |
| **Schéma** | Source + colonnes techniques | Typé, renommé, normalisé | Clés de substitution, mesures, hiérarchies |
| **Mode** | Ajout / remplacement de partition | Incrémental (`merge`) | Incrémental (`merge`) ou table |
| **Partitionnement** | `_ingest_date` | Date métier (`days(event_ts)`) | Date métier (mois) |
| **Données perso** | En clair (pseudonymes source) | **Pseudonymisées (HMAC)** | Pseudonymisées, minimisées |
| **Accès** | `data_engineer`, comptes de service | + `analyst`, `ml_engineer` | + `bi_viewer` |
| **Rétention** | 13 mois (expiration des snapshots) | Illimitée | Illimitée |

**Colonnes techniques Bronze** (toutes tables) : `_ingest_ts`, `_ingest_date`, `_source_file`,
`_batch_id` (exécution Airflow ou micro-lot Spark), `_line_no` (ordre dans le fichier, indispensable pour
départager les événements CDC de même horodatage).

**Conventions de nommage.** Catalogue Trino `lakehouse`, schémas `bronze` / `silver` / `gold`.
Tables : `bronze.<source>`, `silver.stg_<source>`, `silver.int_<objet>`, `gold.dim_<objet>`,
`gold.fct_<processus>`, `gold.mart_<domaine>`.

---

## 6. Flux de données

Le schéma ci-dessous présente les quatre flux de la plateforme ; chacun est détaillé dans les
sous-sections suivantes.

@@SCHEMA:03_flux_de_donnees@@

*Schéma : `docs/diagrammes/03_flux_de_donnees.pdf`.*

### 6.1 Ingestion batch (Airflow) — L3

DAG d'ingestion quotidien (planifié à 02:00, rattrapage possible sur tout l'historique). Pour chaque source :

1. **Attente du fichier** du jour dans la zone d'atterrissage ;
2. **Contrôle du contrat** : colonnes, types et clés conformes au contrat de données YAML ;
3. **Chargement Bronze** : remplacement de la partition du jour (`_ingest_date`) ;
4. **Contrôle de complétude** : nombre de lignes du fichier = nombre de lignes chargées ;
5. **Publication des métriques** (lignes, durée, fraîcheur) ;
6. **Déclenchement de dbt** pour mettre à jour Silver et Gold.

| Exigence | Mise en œuvre |
|---|---|
| **Idempotence** | Remplacement de la partition `_ingest_date` du jour : rejouer un jour remplace ses données sans doublon |
| **Reprise** | 3 nouvelles tentatives avec délai croissant ; écritures atomiques (Iceberg) : un échec ne laisse pas d'état partiel |
| **Rattrapage (backfill)** | Chargement initial de tout l'historique (01/01/2025 → 31/08/2026), puis quotidien |
| **Schéma versionné** | Contrat YAML par source (`quality/contracts/`), rupture de schéma = échec explicite du contrôle du contrat |
| **Sources** | POS, commandes, lignes, retours (quotidien) + clients, CDC, produits, magasins (référentiels) — ≥ 2 sources exigées |

### 6.2 Ingestion temps réel du clickstream (Redpanda → Spark → Bronze) — L3


| Exigence | Mise en œuvre |
|---|---|
| **1 topic, 1 consommateur** | `clickstream.events.v1`, groupe de consommateurs `bronze-clickstream` |
| **Ordre** | Clé de partition = `session_id` → ordre garanti au sein d'une session |
| **Fiabilité** | Point de reprise Spark (checkpoint) + écriture atomique Iceberg → chaque événement écrit *exactement une fois* en Bronze |
| **Messages invalides** | JSON illisible ou champ obligatoire manquant → table de quarantaine (DLQ), jamais de perte silencieuse |
| **Doublons** | Dédoublonnage sur `event_id` en Silver (rejeu producteur possible) |
| **Données tardives** | Tolérance de retard d'1 h (watermark) sur `event_ts` pour les agrégats ; Bronze accepte tout |
| **Métriques** | Retard du consommateur, événements / s, délai événement → Bronze, taux de quarantaine |

### 6.3 Transformation (dbt sur Trino) — L3

```
bronze.*  →  stg_*  (Silver : typage, renommage, pseudonymisation, dédoublonnage, indicateurs qualité)
          →  int_*  (Silver : unions, règles métier, historisation SCD2 clients)
          →  dim_* / fct_*  (Gold : étoile)
          →  mart_*  (Gold : agrégats prêts pour la BI / couche sémantique)
```

Points clés :

- **SCD2 `dim_customer`** : état initial (`customers`) + événements CDC triés par
  `(change_ts, _line_no)`. Les mises à jour multiples d'un même client au même horodatage sont
  réduites à la dernière. Détection des changements par **empreinte (hash) des attributs suivis**
  (`region`, `segment`, `consent_marketing`). Une suppression (`op = D`) ferme la version
  courante et crée une version `is_deleted = true`.
- **Faits incrémentaux** : `materialized='incremental'`, stratégie `merge` sur la clé naturelle,
  fenêtre de relecture de 3 jours pour absorber les arrivées tardives.
- **Environnements** : profils dbt `dev` (schémas préfixés `dev_`) et `prod`, sélectionnés par
  variable d'environnement.

### 6.4 Cas d'usage ML — prévision de la demande — L5

| Élément | Choix |
|---|---|
| Cible | Quantités vendues **par jour et par catégorie de produit**, tous canaux confondus |
| Données | `gold.fct_sales` agrégé (20 mois d'historique ≈ 600 points par série) |
| Référence | Modèle naïf saisonnier (ventes de J-7), pour mesurer l'apport des modèles |
| Modèles | Prophet (saisonnalités hebdo / annuelle) et XGBoost (lags, calendrier, promos) |
| Validation | Validation glissante dans le temps, horizon de 14 jours |
| Métriques | **MAPE (cible < 15 %)**, MAE, RMSE, enregistrées dans MLflow |
| Mise en production | Meilleur modèle enregistré dans le registre de modèles MLflow (`Staging` → `Production`) |
| Prévision | Traitement batch quotidien planifié par Airflow → `gold.fct_sales_forecast` (prévision + intervalle) |
| Suivi | Comparaison prévision vs réalisé en Gold → tableau de bord et alerte si le MAPE dérive |

Choix motivé dans l'[ADR-0007](adr/0007-cas-usage-prevision.md).

### 6.5 BI et couche sémantique — L6

- Superset interroge **uniquement Gold** via Trino (rôle `bi_viewer`).
- **Couche sémantique** : les indicateurs (CA, panier moyen, conversion, taux de retour, MAPE) sont
  définies **une seule fois** dans les `mart_*` dbt et déclarés comme métriques des jeux de données
  Superset. Les tableaux de bord sont déclarés en `exposures` dbt pour tracer le lien BI → Gold.

---

## 7. Modèle analytique Gold

### 7.1 Grain des faits

| Fait | Grain | Sources | Mesures principales |
|---|---|---|---|
| `fct_sales` | **1 ligne = 1 article vendu** (ligne de commande en ligne ou ligne de ticket magasin) | `order_items` + `orders`, `pos_sales` | `qty`, `gross_amount`, `discount_amount`, `net_amount`, `tax_amount`, `cost_amount`, `margin_amount` |
| `fct_orders` | 1 ligne = 1 commande en ligne | `orders` (+ agrégat lignes) | `nb_items`, `order_amount`, `is_cancelled`, `has_no_lines` |
| `fct_returns` | 1 ligne = 1 retour | `returns` | `return_qty`, `return_amount` |
| `fct_web_events` | 1 ligne = 1 événement | `clickstream` | `latency_ms`, compteur |
| `fct_web_sessions` | 1 ligne = 1 session | `clickstream` agrégé | `nb_events`, étapes du tunnel d'achat, `is_converted` |
| `fct_sales_forecast` | 1 ligne = 1 jour × 1 catégorie × 1 version de modèle | sortie du modèle ML | `forecast_qty`, `lower`, `upper`, `actual_qty` |

**Choix structurant** : `fct_sales` **unifie** ventes en ligne et magasin avec une dimension
canal (`web`, `mobile`, `marketplace`, `store`). C'est ce qui rend l'analyse omnicanale directe
(ADR-0008). Les ventes magasin ont `store_sk` renseigné ; les ventes en ligne pointent vers le
membre « En ligne » de `dim_store`.

### 7.2 Dimensions

| Dimension | Type | Clé naturelle | Attributs / hiérarchie |
|---|---|---|---|
| `dim_date` | Type 0 (générée) | date | jour → semaine → mois → trimestre → année ; jour férié, week-end |
| `dim_customer` | **SCD2** | `customer_id` (pseudonymisé) | région, segment, consentement ; `valid_from`, `valid_to`, `is_current`, `is_deleted` |
| `dim_product` | SCD2 (structure prête, 1 version en source) | `product_id` | produit → sous-catégorie → catégorie ; marque, prix, coût, TVA |
| `dim_store` | SCD1 | `store_id` | magasin → ville → format |
| `dim_channel` | Type 0 | `channel` | canal → type (en ligne / physique) |
| `dim_promo` | Type 0 | `promo_code` | taux de remise, famille de promo |

**Membres spéciaux** : clé `-1` « Inconnu » (ex. : 28 % des tickets POS sans client) et `-2`
« Non applicable » (ex. : magasin pour une vente en ligne).

### 7.3 Matrice faits × dimensions (bus matrix)

| Fait \ Dimension | date | client | produit | magasin | canal | promo |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| `fct_sales` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `fct_orders` | ✅ | ✅ | | | ✅ | ✅ |
| `fct_returns` | ✅ | ✅ | ✅ | | ✅ | |
| `fct_web_events` | ✅ | ✅ | ✅ | | ✅ | |
| `fct_web_sessions` | ✅ | ✅ | | | ✅ | |
| `fct_sales_forecast` | ✅ | | ✅ (catégorie) | | | |

### 7.4 Schéma en étoile (cœur des ventes)

@@SCHEMA:04_schema_etoile@@

*Schéma : `docs/diagrammes/04_schema_etoile.pdf`.*

La jointure `fct_sales → dim_customer` est **point-in-time** : la version client retenue est
celle valide à la date de vente (`sale_ts` entre `valid_from` et `valid_to`). Les ventes
d'août 2026 pointent donc vers les versions issues du CDC du 01/08/2026 : c'est la preuve
visible du SCD2.

---

## 8. Catalogue de données et traçabilité (lineage)

| Besoin | Outil | Contenu |
|---|---|---|
| Catalogue technique | Hive Metastore | Tables Iceberg, schémas, partitions, snapshots |
| Catalogue métier | Documentation dbt (publiée sur `datadocs`) | Description de chaque table / colonne, tests, propriétaires |
| Dictionnaire de données | `docs/dictionnaire_donnees.md` : sources (S0), puis complété avec Silver / Gold depuis les YAML dbt | Définition, type, unité, source, sensibilité RGPD |
| Traçabilité des traitements | OpenLineage (Airflow + Spark) → **Marquez** | Fichier source → Bronze → traitements → Silver → Gold |
| Traçabilité des modèles | Documentation dbt (graphe des modèles) + `exposures` | Tables Gold → tableaux de bord Superset |
| Historique | Snapshots Iceberg (retour à une version passée) | Audit et retour arrière d'une table |

---

## 9. Sécurité et RGPD

### 9.1 Classification des données

| Colonne | Source | Classe | Traitement |
|---|---|---|---|
| `customer_id` | customers, orders, pos, clickstream, CDC | Identifiant indirect | **HMAC-SHA256 avec sel secret** dès `stg_` → `customer_hk` |
| `email_pseudo` | customers | Donnée personnelle (pseudonymisée source) | **Non propagée** au-delà de Bronze (minimisation) |
| `phone_pseudo` | customers | Donnée personnelle (pseudonymisée source) | **Non propagée** au-delà de Bronze (minimisation) |
| `consent_marketing` | customers, CDC | Base légale | Conservée, historisée (SCD2) |
| `region`, `segment` | customers | Quasi-identifiant faible | Conservées (granularité régionale) |
| `session_id` | clickstream | Identifiant technique | Conservé (pas de lien direct à une personne) |

Le sel HMAC est stocké hors code (variable d'environnement / secret Airflow, jamais versionné).
Il est commun à toutes les sources pour préserver les jointures.

### 9.2 Gestion des accès (RBAC)

Contrôle d'accès **fichier** de Trino (`rules.json`), rôles Superset, policies MinIO.

| Rôle | Bronze | Silver | Gold | Écriture |
|---|:-:|:-:|:-:|---|
| `data_engineer` | R | R | R | Bronze, Silver, Gold (via comptes de service) |
| `svc_airflow` / `svc_streaming` | R/W | R/W | R/W | Pipelines uniquement |
| `ml_engineer` | — | R | R | `gold.fct_sales_forecast` |
| `analyst` | — | R | R | — |
| `bi_viewer` (Superset) | — | — | R | — |

### 9.3 Journalisation et droits des personnes

- **Audit des requêtes** : event listener Trino → log de chaque requête (utilisateur, tables,
  horodatage), conservé 12 mois.
- **Audit stockage** : logs d'accès MinIO ; logs de tâches Airflow.
- **Droit à l'effacement** : un événement CDC `D` déclenche la clôture logique en Silver / Gold.
  Une procédure de purge (`make gdpr-erase ID=...`) supprime les lignes Bronze concernées
  (`DELETE` Iceberg) puis exécute `expire_snapshots` pour effacer physiquement l'historique.
- **Rétention** : Bronze 13 mois, snapshots Iceberg 7 jours.

---

## 10. Qualité des données et contrats de données

| Niveau | Outil | Exemples de règles |
|---|---|---|
| Contrat d'entrée | Contrat de données YAML par source | Colonnes, types, nullabilité, clé, propriétaire, SLA de livraison |
| Bronze → Silver | Great Expectations | Unicité des clés, domaines (`channel`, `status`, `event_type`), % NULL, volumétrie vs J-1 |
| Silver → Gold | Tests dbt + GE | Intégrité référentielle, `net_amount ≈ qty × prix × (1 − remise)` à ±0,10 €, montants ≥ 0 |
| Gold | GE + tests dbt | Couverture **> 80 % des tables Gold**, fraîcheur, réconciliation CA Gold vs Bronze |

**Anomalies identifiées au profilage et traitement retenu** (détail : [profilage_donnees.md](profilage_donnees.md)) :

| Anomalie | Volume | Traitement |
|---|---|---|
| Tickets POS sans client | 139 630 (28 %) | Membre `-1` « Client anonyme » |
| Commandes sans ligne d'article | 67 689 | Conservées dans `fct_orders`, indicateur `has_no_lines` |
| Retours : couple commande × produit absent des ventes | 99 991 | Rattachement au grain commande, indicateur `line_not_found` |
| Retours datés avant la commande | 49 809 | Quarantaine (`silver.quarantine_returns`) + alerte GE |
| Écart d'arrondi `net_amount` | 110 205 lignes (< 0,10 €) | Tolérance ±0,10 € ; `net_amount` source fait foi |
| CDC : MAJ multiples au même horodatage | 9 043 clients | Ordre de fichier (`_line_no`) pour départager |
| `region` NULL | 100 | Valeur « Non renseigné » + suivi du taux NULL |

Rapports qualité GE et documentation dbt publiés à chaque exécution sur `http://localhost:8082`.

---

## 11. SLO, supervision et alertes — L7

| SLO | Indicateur | Cible | Alerte |
|---|---|---|---|
| **Fraîcheur batch** | Âge de la dernière partition Gold `fct_sales` | Données J-1 disponibles avant 07:00 | > 30 h → critique |
| **Latence streaming** | Délai production → Bronze (p95) | < 2 min | > 5 min pendant 10 min |
| **Fraîcheur web Gold** | Âge de `fct_web_sessions` | < 90 min | > 3 h |
| **Complétude** | Lignes Bronze / lignes fichier source | 100 % | < 100 % → critique |
| **Rejets** | Lignes en quarantaine (y compris DLQ) / total | < 1 % | > 1 % |
| **Qualité** | Contrôles GE critiques en succès sur Gold | 100 % | Tout échec critique |
| **Fiabilité des pipelines** | Exécutions Airflow réussies (7 jours glissants) | ≥ 99 % | Échec après les nouvelles tentatives |
| **Performance ML** | MAPE prévision vs réalisé (7 jours glissants) | < 15 % | > 20 % |

**Collecte** : Airflow → StatsD exporter ; traitements batch, GE et dbt → Pushgateway ; Spark →
`StreamingQueryListener` → Pushgateway ; Redpanda → point d'accès Prometheus natif.
**Restitution** : tableau de bord Grafana « SLO plateforme ».
**Alertes simulées** : règles Prometheus → Alertmanager → webhook (récepteur local qui journalise
les alertes), démontré en soutenance par un incident provoqué.

---

## 12. Environnements, CI/CD et exploitation

| Sujet | Mise en œuvre |
|---|---|
| Environnements | `dev` / `prod` séparés par `.env` + profils dbt + schémas préfixés |
| Démarrage | `make up` (Compose), `make seed` (dépôt des fichiers en zone d'atterrissage), `make demo` (exécution de bout en bout) |
| Intégration continue (GitHub Actions) | Contrôle de style (ruff, sqlfluff), tests unitaires Python, `dbt parse` + `dbt build` sur échantillon (DuckDB), validation des contrats de données, construction des images |
| Déploiement continu | Construction et étiquetage des images, publication de la documentation |
| Reproductibilité | Images versionnées, jeu de données de démarrage, `.env.sample` |
| Documentation | README d'orchestration, ADR, dictionnaire de données, procédures d'incident |

---

## 13. Risques, dette et perspectives (V1)

| Risque | Impact | Mitigation |
|---|---|---|
| Empreinte mémoire de la stack (~13 Go) | Démo instable sur poste léger | Mode `up-lite`, limites mémoire par service, démo sur la machine la mieux dotée |
| Compatibilité des versions (Spark / Iceberg / HMS / Trino) | Blocage S1-S2 | Matrice de versions figée dès S1, tests de démarrage en CI |
| Incohérences des retours (dates, couples absents) | KPI taux de retour biaisé | Quarantaine + indicateurs, KPI calculé au grain commande, limite documentée |
| Absence de données de stock | KPI rupture impossible | Hors périmètre, perspective : flux d'inventaire magasin |
| `gl_entries` datées d'un seul jour | Pas d'analyse financière temporelle | Hors périmètre de la première version, agrégat finance en option |

---

## 14. Décisions d'architecture (ADR)

| ADR | Décision |
|---|---|
| [0001](adr/0001-format-lakehouse-iceberg.md) | Apache Iceberg comme format de table |
| [0002](adr/0002-stockage-minio-hive-metastore.md) | MinIO + Hive Metastore pour le stockage et le catalogue |
| [0003](adr/0003-moteur-sql-trino.md) | Trino comme moteur SQL unique (dbt, GE, BI) |
| [0004](adr/0004-streaming-redpanda-spark.md) | Redpanda + Spark Structured Streaming |
| [0005](adr/0005-transformations-dbt.md) | dbt-trino pour les transformations |
| [0006](adr/0006-pseudonymisation-hmac.md) | Pseudonymisation HMAC en entrée de Silver |
| [0007](adr/0007-cas-usage-prevision.md) | Prévision de la demande comme cas d'usage ML |
| [0008](adr/0008-fait-ventes-omnicanal.md) | Fait de ventes unifié omnicanal |
| [0009](adr/0009-anomalies-quarantaine.md) | Quarantaine et indicateurs plutôt que suppression |
