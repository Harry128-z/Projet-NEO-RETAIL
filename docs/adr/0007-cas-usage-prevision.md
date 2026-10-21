# ADR-0007 — Prévision de la demande comme cas d'usage ML

- **Statut** : accepté
- **Date** : 20/10/2026

## Contexte

Le sujet propose la prévision de la demande ou l'attrition des clients (churn). Les données de retours sont incohérentes (50 % datés avant la commande) ; les données clients sont peu riches (une seule date d'inscription).

## Décision

**Prévision des quantités vendues par jour et par catégorie**, tous canaux.

## Justification

- 20 mois d'historique de ventes propres : base solide pour un modèle de séries temporelles.
- Lien direct avec l'enjeu métier (stocks, promotions) et avec le KPI de la grille (MAPE < 15 %).
- L'attrition (churn) souffrirait de l'absence de signal fiable (dates d'inscription identiques, pas de désabonnement explicite).

## Conséquences

- Une référence naïve saisonnière (ventes de J-7) est obligatoire pour démontrer l'apport du modèle.
