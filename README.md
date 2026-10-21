# NeoRetail — Plateforme Data Omnicanale (lakehouse)

Projet M2 Data Engineer — mise en situation professionnelle.

Plateforme lakehouse Bronze / Silver / Gold : ingestion batch (Airflow) et temps réel
(Redpanda + Spark Structured Streaming), transformations (dbt → schéma en étoile),
qualité (Great Expectations, contrats de données), prévision de la demande (MLflow),
tableaux de bord (Superset) et supervision (Prometheus / Grafana).

## Structure du dépôt

| Dossier | Contenu |
|---|---|
| `infra/` | Docker Compose et configuration des outils |
| `dags/` | DAG Airflow (ingestion batch, transformations, ML) |
| `streaming/` | Producteur et consommateur du flux clickstream |
| `dbt/` | Modèles `stg_` → `int_` → `dim_` / `fct_` (Silver → Gold) |
| `quality/` | Contrats de données YAML et règles Great Expectations |
| `ml/` | Entraînement, suivi MLflow, prévision quotidienne |
| `bi/` | Exports des tableaux de bord Superset |
| `docs/` | Dossier d'architecture (L1), schémas PDF, ADR, profilage, dictionnaire de données |
| `scripts/` | Utilitaires (profilage, génération de la documentation, découpage des fichiers) |

Les dossiers exigés par le sujet (`/infra`, `/dags`, `/dbt`, `/quality`, `/ml`, `/bi`, `/docs`) sont tous
présents. `streaming/` et `scripts/` sont ajoutés pour séparer clairement le code temps réel et les utilitaires.
Chaque dossier contient un README qui décrit son contenu et le jalon auquel il est rempli.

## Conformité au sujet

| Exigence du sujet | Emplacement | État |
|---|---|---|
| **L1** — Dossier d'architecture (PDF) : diagrammes logique / physique, flux, choix motivés, sécurité / RGPD | `docs/L1_dossier_architecture.pdf` + `docs/diagrammes/*.pdf` |Version S0 (mise à jour à chaque jalon) |
| Décisions d'architecture (ADR courts) | `docs/adr/` |  9 ADR |
| Dictionnaire de données | `docs/dictionnaire_donnees.md` |  Sources (Silver / Gold en S3-S4) |
| **L2** — Dépôt Git structuré + README d'orchestration + Makefile | ce dépôt |  Structure faite ; Makefile et démarrage en S1 |
| `.env.sample` + instructions de démarrage Docker Compose | racine + `infra/` | S1 |
| **L3** — DAG Airflow d'ingestion batch (≥ 2 sources) | `dags/` | S1 |
| **L3** — Streaming : 1 topic clickstream, 1 consommateur, écriture en Bronze | `streaming/` | S2 |
| **L3** — Modèles dbt `stg_`, `int_`, `dim_`, `fct_` jusqu'à Gold | `dbt/` | S3 |
| **L4** — Règles Great Expectations, rapports publiés, contrats de données YAML | `quality/` | S1 (contrats) et S4 |
| **L5** — Pipeline ML avec suivi MLflow + job de prévision | `ml/` | S5 |
| **L6** — Tableau de bord BI (3 à 5 KPI) | `bi/` | S6 |
| **L7** — Supervision : fraîcheur, latence, erreurs, alertes simulées | `infra/` | S7 |
| CI/CD (GitHub Actions) | `.github/workflows/` | S7 |
| **L8** — Soutenance + post-mortem (3 risques et plans d'action) | `docs/` | S8 |

## Documentation
- [Schémas (PDF)](docs/diagrammes/)
- [Décisions d'architecture (ADR)](docs/adr/)
- [Profilage des données sources](docs/profilage_donnees.md)
- [Dictionnaire de données](docs/dictionnaire_donnees.md)

## Données

Les données sources (`neoretail_bigdata_pack`) ne sont pas versionnées dans Git : les placer dans `data/`.

## Démarrage

Les instructions de démarrage (`make up`) seront ajoutées en S1.
