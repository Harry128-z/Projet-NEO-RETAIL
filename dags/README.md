# Orchestration Airflow

Les DAG Airflow : les « plannings » qui enchaînent les tâches automatiquement.

## Contenu prévu

- DAG d'ingestion batch (au moins 2 sources) → zone Bronze
- DAG de transformation (lancement de dbt) et de contrôle qualité
- DAG de prévision ML (inférence quotidienne)

**Jalon** : S1 (ingestion batch), S3-S5 (dbt, qualité, ML)  
**Livrable du sujet** : L3
