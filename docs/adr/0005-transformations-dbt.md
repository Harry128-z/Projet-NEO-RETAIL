# ADR-0005 — dbt-trino pour les transformations

- **Statut** : accepté
- **Date** : 20/10/2026

## Contexte

Les transformations vont jusqu'à un schéma en étoile Gold, avec tests, documentation et traçabilité (lineage).

## Décision

**dbt** (adaptateur Trino), couches `stg_` → `int_` → `dim_` / `fct_` → `mart_`.

## Justification

- SQL versionné, testable (tests génériques + singuliers) et documenté.
- La documentation dbt fournit le catalogue métier et la traçabilité ; les `exposures` relient Gold aux tableaux de bord.
- Chargement incrémental par fusion (`merge`) sur Iceberg : idempotence et performances.
- Profils `dev` / `prod` pour la séparation des environnements.

## Conséquences

- Le SCD2 clients est implémenté en modèle incrémental dédié plutôt qu'en `snapshot` dbt, car le CDC fourni contient plusieurs changements au même horodatage.
