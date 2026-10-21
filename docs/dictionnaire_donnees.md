# Dictionnaire de données — sources NeoRetail

Description de chaque colonne des fichiers sources du pack `neoretail_bigdata_pack`.
Ce dictionnaire sera complété avec les tables Silver et Gold à partir des fichiers YAML dbt (S3-S4).

**Légende de la colonne RGPD** :

- **Identifiant indirect** : permet de relier des données à une personne ; remplacé par un code pseudonyme (HMAC) dès la zone Silver.
- **Donnée personnelle** : déjà pseudonymisée par la source ; conservée uniquement en Bronze (accès restreint), jamais propagée au-delà (minimisation).
- **—** : donnée non personnelle.

Les exemples sont tirés de la première ligne de chaque fichier ; les données personnelles sont masquées.

## Sommaire

1. Ventes magasins — `pos_sales`
2. Commandes en ligne (en-têtes) — `orders`
3. Lignes de commandes en ligne — `order_items`
4. Retours — `returns`
5. Référentiel clients — `customers`
6. Changements clients (CDC) — `customer_updates`
7. Catalogue produits — `products`
8. Référentiel magasins — `stores`
9. Navigation web (clickstream) — `clickstream`

## 1. Ventes magasins — `pos_sales`

Une ligne par article scanné en caisse dans un magasin NeoRetail.

| Propriété | Valeur |
|---|---|
| Fichier source | `raw/pos/pos_sales.csv.gz` (CSV compressé) |
| Volume | 500 000 lignes |
| Mode d'ingestion | batch, livraison quotidienne |
| Clé primaire | `sale_id` |
| Date métier | `sale_ts` |
| Propriétaire | Équipe Magasins |

| Colonne | Type | Obligatoire | Description | Règles / valeurs autorisées | RGPD | Exemple |
|---|---|:-:|---|---|---|---|
| `sale_id` | texte | oui | Identifiant de la ligne de ticket | « PS » + 10 chiffres | — | `PS0000000001` |
| `sale_ts` | horodatage | oui | Horodatage du passage en caisse | — | — | `2025-11-14T21:12:20` |
| `store_id` | texte | oui | Magasin | « S » + 4 chiffres | — | `S0121` |
| `customer_id` | texte | non | Client carte fidélité (NULL = client anonyme) | « C » + 8 chiffres | Identifiant indirect | `C00074559` |
| `product_id` | texte | oui | Produit | « P » + 7 chiffres | — | `P0001471` |
| `qty` | entier | oui | Quantité | ≥ 1 | — | `6` |
| `unit_price` | décimal | oui | Prix unitaire | ≥ 0 ; unité : EUR | — | `18.23` |
| `discount_rate` | décimal | oui | Taux de remise | ≥ 0 ; ≤ 1 | — | `0.00` |
| `net_amount` | décimal | oui | Montant net de la ligne | ≥ 0 ; unité : EUR | — | `109.39` |

## 2. Commandes en ligne (en-têtes) — `orders`

Une ligne par commande passée sur le site web, l'application mobile ou la marketplace.

| Propriété | Valeur |
|---|---|
| Fichier source | `raw/orders/orders.csv.gz` (CSV compressé) |
| Volume | 500 000 lignes |
| Mode d'ingestion | batch, livraison quotidienne |
| Clé primaire | `order_id` |
| Date métier | `order_ts` |
| Propriétaire | Équipe E-commerce |

| Colonne | Type | Obligatoire | Description | Règles / valeurs autorisées | RGPD | Exemple |
|---|---|:-:|---|---|---|---|
| `order_id` | texte | oui | Identifiant de commande | « O » + 10 chiffres | — | `O0000000001` |
| `order_ts` | horodatage | oui | Horodatage de la commande | — | — | `2026-03-09T02:34:37` |
| `customer_id` | texte | oui | Client | « C » + 8 chiffres | Identifiant indirect | `C00052834` |
| `channel` | texte | oui | Canal de vente | web, mobile, marketplace | — | `marketplace` |
| `payment_method` | texte | oui | Moyen de paiement | card, wallet, transfer, gift_card | — | `card` |
| `status` | texte | oui | Statut de la commande | paid, shipped, delivered, cancelled | — | `paid` |
| `promo_code` | texte | oui | Code promo (NONE si aucun) | NONE, LOYAL5, WELCOME10, FLASH15, SUMMER20 | — | `NONE` |

## 3. Lignes de commandes en ligne — `order_items`

Une ligne par produit d'une commande en ligne. Livrée avec les commandes du même jour métier.

| Propriété | Valeur |
|---|---|
| Fichier source | `raw/orders/order_items.csv.gz` (CSV compressé) |
| Volume | 1 000 000 lignes |
| Mode d'ingestion | batch, livraison quotidienne |
| Clé primaire | `order_item_id` |
| Date métier | `order_ts` |
| Propriétaire | Équipe E-commerce |

| Colonne | Type | Obligatoire | Description | Règles / valeurs autorisées | RGPD | Exemple |
|---|---|:-:|---|---|---|---|
| `order_item_id` | entier | oui | Identifiant de ligne | ≥ 1 | — | `1` |
| `order_id` | texte | oui | Commande parente | « O » + 10 chiffres | — | `O0000311489` |
| `product_id` | texte | oui | Produit | « P » + 7 chiffres | — | `P0005236` |
| `qty` | entier | oui | Quantité | ≥ 1 | — | `4` |
| `unit_price` | décimal | oui | Prix unitaire | ≥ 0 ; unité : EUR | — | `29.36` |
| `discount_rate` | décimal | oui | Taux de remise | ≥ 0 ; ≤ 1 | — | `0.00` |
| `net_amount` | décimal | oui | Montant net de la ligne | ≥ 0 ; unité : EUR | — | `117.44` |

## 4. Retours — `returns`

Une ligne par retour de produit enregistré par l'entrepôt.

| Propriété | Valeur |
|---|---|
| Fichier source | `raw/returns/returns.csv.gz` (CSV compressé) |
| Volume | 100 000 lignes |
| Mode d'ingestion | batch, livraison quotidienne |
| Clé primaire | `return_id` |
| Date métier | `return_ts` |
| Propriétaire | Équipe Logistique |

| Colonne | Type | Obligatoire | Description | Règles / valeurs autorisées | RGPD | Exemple |
|---|---|:-:|---|---|---|---|
| `return_id` | texte | oui | Identifiant du retour | « R » + 9 chiffres | — | `R000000001` |
| `return_ts` | horodatage | oui | Horodatage de réception du retour | — | — | `2025-10-12T01:23:37` |
| `order_id` | texte | oui | Commande d'origine | « O » + 10 chiffres | — | `O0000414893` |
| `product_id` | texte | oui | Produit retourné | « P » + 7 chiffres | — | `P0008136` |
| `return_qty` | entier | oui | Quantité retournée | ≥ 1 | — | `2` |
| `reason` | texte | oui | Motif | late, wrong_item, damaged, size_issue, not_as_expected, other | — | `late` |
| `return_amount` | décimal | oui | Montant remboursé | ≥ 0 ; unité : EUR | — | `94.29` |

## 5. Référentiel clients — `customers`

Photo complète du référentiel clients. Les changements ultérieurs arrivent par le flux CDC customer_updates.

| Propriété | Valeur |
|---|---|
| Fichier source | `raw/customers/customers.csv.gz` (CSV compressé) |
| Volume | 100 000 lignes |
| Mode d'ingestion | batch, livraison photo complète ponctuelle |
| Clé primaire | `customer_id` |
| Date métier | aucune (photo au 2025-01-01) |
| Propriétaire | Équipe CRM (relation client) |

| Colonne | Type | Obligatoire | Description | Règles / valeurs autorisées | RGPD | Exemple |
|---|---|:-:|---|---|---|---|
| `customer_id` | texte | oui | Identifiant client | « C » + 8 chiffres | Identifiant indirect | `C00000001` |
| `customer_key` | entier | oui | Clé technique source | — | — | `1` |
| `region` | texte | non | Région (quelques NULL connus) | IDF, Nord, Est, Ouest, Sud-Est, Sud-Ouest, Centre, International | — | `IDF` |
| `segment` | texte | oui | Segment client | Standard, Premium, Etudiant, Entreprise | — | `Standard` |
| `signup_date` | date | oui | Date d'inscription | — | — | `2025-01-01` |
| `consent_marketing` | booléen | oui | Consentement marketing (base légale RGPD) | — | — | `false` |
| `email_pseudo` | texte | oui | E-mail pseudonymisé à la source — non propagé après Bronze | — | Donnée personnelle | (masqué) |
| `phone_pseudo` | texte | oui | Téléphone pseudonymisé à la source — non propagé après Bronze | — | Donnée personnelle | (masqué) |
| `is_active` | booléen | oui | Client actif | — | — | `false` |

## 6. Changements clients (CDC) — `customer_updates`

Changements du référentiel clients (U = mise à jour, D = suppression). Source de l'historisation SCD2.

| Propriété | Valeur |
|---|---|
| Fichier source | `cdc/customer_updates.jsonl.gz` (JSONL compressé) |
| Volume | 50 000 lignes |
| Mode d'ingestion | batch, livraison à chaque lot de changements |
| Clé primaire | aucune (plusieurs événements possibles par client) |
| Date métier | `change_ts` |
| Propriétaire | Équipe CRM (relation client) |

| Colonne | Type | Obligatoire | Description | Règles / valeurs autorisées | RGPD | Exemple |
|---|---|:-:|---|---|---|---|
| `op` | texte | oui | Type d'opération | U, D | — | `U` |
| `customer_id` | texte | oui | Client concerné | « C » + 8 chiffres | Identifiant indirect | `C00097314` |
| `change_ts` | horodatage | oui | Horodatage du changement | — | — | `2026-08-01T12:00:00` |
| `new_region` | texte | non | Nouvelle région | IDF, Nord, Est, Ouest, Sud-Est, Sud-Ouest, Centre, International | — | `International` |
| `new_segment` | texte | non | Nouveau segment | Standard, Premium, Etudiant, Entreprise | — | `Entreprise` |
| `new_consent_marketing` | booléen | non | Nouveau consentement | — | — | `true` |

## 7. Catalogue produits — `products`

Photo complète du catalogue produits.

| Propriété | Valeur |
|---|---|
| Fichier source | `raw/products/products.csv.gz` (CSV compressé) |
| Volume | 20 000 lignes |
| Mode d'ingestion | batch, livraison photo complète ponctuelle |
| Clé primaire | `product_id` |
| Date métier | aucune (photo au 2025-01-01) |
| Propriétaire | Équipe Offre produits |

| Colonne | Type | Obligatoire | Description | Règles / valeurs autorisées | RGPD | Exemple |
|---|---|:-:|---|---|---|---|
| `product_id` | texte | oui | Identifiant produit | « P » + 7 chiffres | — | `P0000001` |
| `product_key` | entier | oui | Clé technique source | — | — | `1` |
| `sku` | texte | oui | Référence article | « SKU- » + 8 chiffres | — | `SKU-00000001` |
| `category` | texte | oui | Catégorie | Beauty, Electronics, Sports, Fashion, Grocery, Home | — | `Beauty` |
| `subcategory` | texte | oui | Sous-catégorie | A, B, C, D | — | `A` |
| `brand` | texte | oui | Marque | — | — | `Brand_391` |
| `unit_cost` | décimal | oui | Coût d'achat unitaire | ≥ 0 ; unité : EUR | — | `48.99` |
| `list_price` | décimal | oui | Prix catalogue | ≥ 0 ; unité : EUR | — | `87.37` |
| `vat_rate` | décimal | oui | Taux de TVA | 0.055, 0.1, 0.2 | — | `0.2` |
| `is_active` | booléen | oui | Produit actif | — | — | `true` |
| `effective_from` | date | oui | Début de validité | — | — | `2025-01-01` |
| `effective_to` | date | non | Fin de validité (NULL = version courante) | — | — | *vide* |
| `is_current` | booléen | oui | Version courante | — | — | `true` |

## 8. Référentiel magasins — `stores`

Photo complète des magasins NeoRetail.

| Propriété | Valeur |
|---|---|
| Fichier source | `raw/stores/stores.csv.gz` (CSV compressé) |
| Volume | 200 lignes |
| Mode d'ingestion | batch, livraison photo complète ponctuelle |
| Clé primaire | `store_id` |
| Date métier | aucune (photo au 2025-01-01) |
| Propriétaire | Équipe Magasins |

| Colonne | Type | Obligatoire | Description | Règles / valeurs autorisées | RGPD | Exemple |
|---|---|:-:|---|---|---|---|
| `store_id` | texte | oui | Identifiant magasin | « S » + 4 chiffres | — | `S0001` |
| `store_key` | entier | oui | Clé technique source | — | — | `1` |
| `city` | texte | oui | Ville | — | — | `Bordeaux` |
| `format` | texte | oui | Format de magasin | proximity, super, hyper, outlet | — | `super` |
| `is_active` | booléen | oui | Magasin ouvert | — | — | `true` |

## 9. Navigation web (clickstream) — `clickstream`

Un événement de navigation web / mobile. Publié dans le topic clickstream.events.v1.

| Propriété | Valeur |
|---|---|
| Fichier source | `stream/clickstream.jsonl.gz` (JSONL compressé) |
| Volume | 1 000 000 lignes |
| Mode d'ingestion | temps réel (Redpanda) |
| Clé primaire | `event_id` |
| Date métier | `event_ts` |
| Propriétaire | Équipe Digital |

| Colonne | Type | Obligatoire | Description | Règles / valeurs autorisées | RGPD | Exemple |
|---|---|:-:|---|---|---|---|
| `event_id` | texte | oui | Identifiant d'événement | « E » + 12 chiffres | — | `E000000000001` |
| `event_ts` | horodatage | oui | Horodatage de l'événement | — | — | `2025-05-30T00:34:05` |
| `session_id` | texte | oui | Session de navigation | — | — | `SESS0000373963` |
| `customer_id` | texte | oui | Client | « C » + 8 chiffres | Identifiant indirect | `C00096372` |
| `event_type` | texte | oui | Type d'événement | page_view, product_view, search, add_to_cart, checkout, purchase | — | `search` |
| `product_id` | texte | non | Produit (NULL pour les pages sans produit) | « P » + 7 chiffres | — | *vide* |
| `device` | texte | oui | Appareil | desktop, mobile, tablet | — | `desktop` |
| `source` | texte | oui | Source de trafic | direct, seo, ads, social, email | — | `direct` |
| `latency_ms` | entier | oui | Latence de chargement (ms) | ≥ 0 | — | `115` |

## Source hors périmètre de la première version

`raw/erp/gl_entries.csv.gz` (100 000 écritures comptables : `entry_id`, `posting_date`, `account_code`, `cost_center`, `document_type`, `amount`, `currency`). Toutes les écritures sont datées du 01/01/2025 (voir profilage, anomalie A8) : aucune analyse financière dans le temps n'est possible. Source non ingérée pour l'instant.
