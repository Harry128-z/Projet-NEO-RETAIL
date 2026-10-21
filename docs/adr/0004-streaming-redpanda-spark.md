# ADR-0004 — Redpanda + Spark Structured Streaming

- **Statut** : accepté
- **Date** : 20/10/2026

## Contexte

Le sujet impose Kafka (ou Redpanda) avec un consommateur Python ou Spark Structured Streaming et une écriture en zone Bronze.

## Décision

**Redpanda** comme file de messages, **Spark Structured Streaming** comme consommateur, écriture en Iceberg Bronze.

## Justification

- Redpanda : API Kafka 100 % compatible, binaire unique sans ZooKeeper, empreinte mémoire bien plus faible.
- Spark Structured Streaming : points de reprise (checkpoints) + écritures atomiques Iceberg → chaque événement écrit exactement une fois en Bronze.
- Gestion native des données en retard (watermark) et des messages invalides (routage vers une table de quarantaine).

## Conséquences

- Spark ajoute environ 2 Go de RAM et une dépendance aux bibliothèques Iceberg / Kafka, dont il faut figer les versions.
