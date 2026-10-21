# ADR-0002 — MinIO + Hive Metastore pour le stockage et le catalogue

- **Statut** : accepté
- **Date** : 20/10/2026

## Contexte

L'architecture doit être cloud-agnostic et tourner en local.

## Décision

**MinIO** (API S3) pour tout le stockage objet, **Hive Metastore** (backend PostgreSQL) comme catalogue technique.

## Justification

- MinIO expose l'API S3 : le même code fonctionne sur AWS S3, et via passerelle sur GCS ou ADLS.
- Hive Metastore est l'équivalent local de AWS Glue Catalog, explicitement demandé par le sujet.
- Les deux sont supportés nativement par Trino, Spark et PyIceberg.

## Conséquences

- Un PostgreSQL unique héberge plusieurs bases (metastore, Airflow, Superset, MLflow, Marquez) pour limiter l'empreinte ; en production, ces bases seraient séparées.
