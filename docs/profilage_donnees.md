# Profilage des données sources

Pack `neoretail_bigdata_pack` (synthétique, pseudonymisé). Résultats reproductibles avec :

```bash
python scripts/profilage_donnees.py data/neoretail_bigdata_pack
```

## 1. Volumes et période

| Source | Lignes | Période | Colonnes avec NULL |
|---|---:|---|---|
| stores | 200 | — | aucune |
| products | 20 000 | — | `effective_to` (100 %, attendu : version courante) |
| customers | 100 000 | `signup_date` = 01/01/2025 pour tous | `region` (0,10 % = 100 lignes) |
| orders | 500 000 | 01/01/2025 → 31/08/2026 | aucune |
| order_items | 1 000 000 | (via orders) | aucune |
| pos_sales | 500 000 | 01/01/2025 → 31/08/2026 | `customer_id` (27,93 %) |
| returns | 100 000 | 01/01/2025 → 31/08/2026 | aucune |
| gl_entries | 100 000 | 01/01/2025 uniquement | aucune |
| clickstream | 1 000 000 | 01/01/2025 → 31/08/2026 | `product_id` (52,07 %, attendu : pages sans produit) |
| customer_updates (CDC) | 50 000 | `change_ts` = 01/08/2026 12:00 pour tous | aucune |

## 2. Clés et intégrité référentielle

- **Unicité** : aucune clé primaire en doublon (stores, products, customers, orders, order_items,
  pos_sales, returns, gl_entries, clickstream).
- **Intégrité référentielle** : 0 orphelin sur toutes les relations testées
  (order_items → orders / products, orders → customers, pos_sales → stores,
  returns → orders, clickstream → customers).

## 3. Domaines de valeurs

| Colonne | Valeurs |
|---|---|
| `orders.channel` | web (224 641), mobile (199 616), marketplace (75 743) |
| `orders.status` | delivered (409 989), shipped (50 148), paid (24 829), cancelled (15 034) |
| `orders.promo_code` | NONE, LOYAL5, WELCOME10, FLASH15, SUMMER20 |
| `order_items.discount_rate` | 0, 0,05, 0,10, 0,15, 0,20 |
| `clickstream.event_type` | page_view, product_view, search, add_to_cart, checkout, purchase |
| `returns.reason` | late, wrong_item, damaged, size_issue, not_as_expected, other (≈ équirépartis) |
| `customers.segment` | Standard, Premium, Etudiant, Entreprise |
| `customers.region` | IDF, Sud-Est, Ouest, Sud-Ouest, Nord, Est, Centre, International, NULL |
| `stores.format` | proximity, super, hyper, outlet |
| `customer_updates.op` | U (49 014), D (986) |

## 4. Anomalies et décisions

| # | Anomalie | Volume | Impact | Décision |
|---|---|---:|---|---|
| A1 | Tickets POS sans `customer_id` | 139 630 | Ventes anonymes en magasin | Membre `-1` « Client anonyme » dans `dim_customer` |
| A2 | Commandes sans aucune ligne d'article | 67 689 | Pas de montant | Conservées dans `fct_orders`, indicateur `has_no_lines` ; exclues du panier moyen |
| A3 | Retours dont le couple (commande, produit) n'existe pas dans `order_items` | 99 991 | Rattachement ligne impossible | Retour rattaché au grain commande, indicateur `line_not_found` |
| A4 | Retours datés avant la commande | 49 809 | Incohérence temporelle | Quarantaine `silver.quarantine_returns` + règle GE |
| A5 | Écart `net_amount` vs `qty × unit_price × (1 − discount_rate)` | 45 433 (web) + 64 772 (POS) | Arrondi au centime (aucun écart > 0,10 €) | Tolérance ±0,10 € ; `net_amount` source fait foi |
| A6 | CDC : plusieurs mises à jour d'un même client au même `change_ts` | 9 043 clients | SCD2 non déterministe | Départage par ordre de fichier (`_line_no`), dernière valeur retenue |
| A7 | `region` NULL | 100 | Segmentation incomplète | Valeur « Non renseigné » + suivi du taux NULL |
| A8 | `gl_entries.posting_date` et `customers.signup_date` sur une seule date | 100 % | Pas d'analyse temporelle | Hors périmètre de la première version (finance) ; pas d'ancienneté client exploitable |
| A9 | Produits : une seule version (`is_current = true` partout) | 20 000 | SCD2 produit non démontrable | Structure SCD2 prête ; démonstration SCD2 sur les clients |

## 5. Ordres de grandeur

- CA net en ligne (`order_items`) : **138,0 M€** ; CA net magasins (`pos_sales`) : **91,3 M€**.
- Clickstream : 59 702 événements `purchase` pour 1 M d'événements. Le clickstream n'est **pas
  relié aux commandes** (pas d'`order_id`) : la conversion se mesure au niveau session.
