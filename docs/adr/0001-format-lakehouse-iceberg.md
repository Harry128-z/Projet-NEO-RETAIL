# ADR-0001 — Apache Iceberg comme format de table

- **Statut** : accepté
- **Date** : 20/10/2026

## Contexte

Le sujet impose un lakehouse Delta, Iceberg ou Hudi avec un metastore « Hive/Glue-like ». Les tables doivent être lisibles par Spark (streaming) et par un moteur SQL (dbt, BI).

## Décision

**Apache Iceberg** (fichiers Parquet), catalogué dans Hive Metastore.

## Justification

- Support natif et mature côté Trino **et** Spark, sans dépendance à un éditeur.
- Évolution de schéma et de partitionnement sans réécriture, partitionnement implicite (`days(event_ts)`).
- Snapshots (retour à une version passée) : audit, retour arrière, purge RGPD via `expire_snapshots`.
- Delta est plus lié à Spark / Databricks côté écosystème ; Hudi est plus complexe à opérer pour un usage majoritairement batch.

## Conséquences

- Maintenance à prévoir : compaction (`optimize`) et expiration des snapshots planifiées dans Airflow.
