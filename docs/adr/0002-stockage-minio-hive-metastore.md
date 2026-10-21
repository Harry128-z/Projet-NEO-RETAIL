 — MinIO + Hive Metastore pour le stockage et le catalogue

 Contexte

L'architecture doit être cloud-agnostic et tourner en local.

Décision

MinIO (API S3) pour tout le stockage objet, **Hive Metastore** (backend PostgreSQL) comme catalogue technique.
 
 Justification

- MinIO expose l'API S3 : le même code fonctionne sur AWS S3, et via passerelle sur GCS ou ADLS.
- Hive Metastore est l'équivalent local de AWS Glue Catalog, explicitement demandé par le sujet.
- Les deux sont supportés nativement par Trino, Spark et PyIceberg.
