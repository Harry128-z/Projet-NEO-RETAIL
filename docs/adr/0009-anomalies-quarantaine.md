# ADR-0009 — Quarantaine et indicateurs plutôt que suppression

- **Statut** : accepté
- **Date** : 20/10/2026

## Contexte

Le profilage révèle des anomalies : tickets sans client, commandes sans lignes, retours incohérents, écarts d'arrondi.

## Décision

Aucune ligne n'est supprimée silencieusement : les lignes **inexploitables** vont en table de quarantaine, les lignes **exploitables mais imparfaites** sont conservées avec un indicateur qualité.

## Justification

- Traçabilité complète : chaque écart est mesurable et expliqué.
- Les KPIs restent réconciliables avec les sources (CA Gold vs Bronze).
- Les taux de quarantaine alimentent directement les SLO de qualité.

## Conséquences

- Les seuils (ex. tolérance ±0,10 € sur `net_amount`) sont versionnés dans les contrats de données.
