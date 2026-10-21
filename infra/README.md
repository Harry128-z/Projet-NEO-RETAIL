# Infrastructure

Tout ce qui permet de lancer la plateforme sur une machine avec Docker Compose.

## Contenu prévu

- `docker-compose.yml` : définition de tous les services (MinIO, Trino, Airflow, Redpanda…)
- Configuration de chaque outil (Trino, Hive Metastore, Prometheus, Grafana…)
- Images Docker personnalisées (Dockerfile)

**Jalon** : S1 (socle : stockage, catalogue, Trino, Airflow), puis enrichi en S2, S5, S6 et S7  
**Livrable du sujet** : L2
