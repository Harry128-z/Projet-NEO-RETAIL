# Ingestion temps réel

Le flux clickstream : du fichier d'événements jusqu'à la zone Bronze.

## Contenu prévu

- Producteur Python qui publie les événements dans le topic Redpanda
- Consommateur Spark Structured Streaming qui écrit en Bronze (+ table de quarantaine)

**Jalon** : S2  
**Livrable du sujet** : L3 (topologie streaming : 1 topic, 1 consommateur, écriture en Bronze)
