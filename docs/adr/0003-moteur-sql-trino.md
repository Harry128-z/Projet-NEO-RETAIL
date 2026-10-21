# ADR-0003 — Trino comme moteur SQL unique

- **Statut** : accepté
- **Date** : 20/10/2026

## Contexte

dbt, Great Expectations et Superset ont besoin d'un moteur SQL sur les tables Iceberg.

## Décision

**Trino** sert de point d'accès SQL unique au lakehouse.

## Justification

- Un seul moteur pour transformer (dbt-trino), contrôler (GE via SQLAlchemy) et restituer (Superset) : une seule politique d'accès.
- Contrôle d'accès par fichier (RBAC) et event listener pour l'audit des requêtes.
- Plus léger à opérer qu'un Spark Thrift Server pour des requêtes interactives.

## Conséquences

- Spark reste utilisé uniquement pour le streaming. Mémoire de Trino à borner (3 Go) en local.
