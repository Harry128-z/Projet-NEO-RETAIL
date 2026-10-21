# Transformations dbt

Les transformations SQL de Bronze vers Silver puis Gold.

## Contenu prévu

- Modèles `stg_` (Silver), `int_` (Silver), `dim_` et `fct_` (Gold), `mart_` (indicateurs BI)
- Tests dbt et description des tables / colonnes (documentation et traçabilité)
- Profils `dev` / `prod`

**Jalon** : S3 (Silver, premières dimensions et faits), S6 (couche sémantique)  
**Livrable du sujet** : L3 (modèles stg_, int_, dim_, fct_ jusqu'à Gold)
