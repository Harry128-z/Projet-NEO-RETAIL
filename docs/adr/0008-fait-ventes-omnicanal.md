# ADR-0008 — Fait de ventes unifié omnicanal

- **Statut** : accepté
- **Date** : 20/10/2026

## Contexte

Les ventes proviennent de deux systèmes : commandes en ligne (en-tête + lignes) et tickets de caisse.

## Décision

Un fait unique **`fct_sales`** au grain de l'article vendu, alimenté par les deux sources, avec une dimension canal (`web`, `mobile`, `marketplace`, `store`). Un fait complémentaire `fct_orders` porte le grain commande.

## Justification

- Les KPIs omnicanaux (CA, mix canal, panier) se calculent sans `UNION` côté BI.
- Grain identique et mesures conformes (`qty`, `net_amount`, remise) dans les deux sources.

## Conséquences

- Les attributs spécifiques (statut de commande, magasin) sont portés par des dimensions avec membres « Non applicable ».
