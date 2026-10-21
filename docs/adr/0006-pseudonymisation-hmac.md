# ADR-0006 — Pseudonymisation HMAC en entrée de Silver

- **Statut** : accepté
- **Date** : 20/10/2026

## Contexte

Le RGPD impose minimisation et pseudonymisation. `customer_id` est présent dans 5 sources ; e-mail et téléphone (déjà pseudonymisés par la source) dans le référentiel clients.

## Décision

`customer_id` est remplacé par `customer_hk = HMAC-SHA256(sel, customer_id)` dans **tous** les modèles `stg_`. E-mail et téléphone ne sont **pas** propagés au-delà de Bronze.

## Justification

- Le HMAC avec sel secret empêche la ré-identification par force brute (contrairement à un hash simple).
- Un sel commun à toutes les sources préserve les jointures.
- Bronze, seule zone contenant des identifiants en clair, est réservée aux ingénieurs et comptes de service.

## Conséquences

- Rotation du sel = recalcul complet de Silver / Gold (documenté dans un runbook).
