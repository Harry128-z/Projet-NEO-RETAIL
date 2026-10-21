"""Profilage des données sources NeoRetail (DuckDB).

Usage : python scripts/profilage_donnees.py data/neoretail_bigdata_pack
Affiche volumes, % de NULL, unicité des clés, intégrité référentielle
et règles métier. Résultats repris dans docs/profilage_donnees.md.
"""
import sys
from pathlib import Path

import duckdb

SOURCES = {
    "stores": "raw/stores/stores.csv.gz",
    "orders": "raw/orders/orders.csv.gz",
    "order_items": "raw/orders/order_items.csv.gz",
    "customers": "raw/customers/customers.csv.gz",
    "returns": "raw/returns/returns.csv.gz",
    "products": "raw/products/products.csv.gz",
    "pos_sales": "raw/pos/pos_sales.csv.gz",
    "gl_entries": "raw/erp/gl_entries.csv.gz",
}
JSON_SOURCES = {
    "clickstream": "stream/clickstream.jsonl.gz",
    "customer_updates": "cdc/customer_updates.jsonl.gz",
}

PRIMARY_KEYS = {
    "stores": "store_id", "orders": "order_id", "order_items": "order_item_id",
    "customers": "customer_id", "returns": "return_id", "products": "product_id",
    "pos_sales": "sale_id", "gl_entries": "entry_id", "clickstream": "event_id",
}

CHECKS = {
    # intégrité référentielle
    "order_items orphelins (order_id)":
        "select count(*) from order_items where order_id not in (select order_id from orders)",
    "order_items orphelins (product_id)":
        "select count(*) from order_items where product_id not in (select product_id from products)",
    "orders orphelins (customer_id)":
        "select count(*) from orders where customer_id not in (select customer_id from customers)",
    "pos_sales orphelins (store_id)":
        "select count(*) from pos_sales where store_id not in (select store_id from stores)",
    "returns orphelins (order_id)":
        "select count(*) from returns where order_id not in (select order_id from orders)",
    "clickstream orphelins (customer_id)":
        "select count(*) from clickstream where customer_id not in (select customer_id from customers)",
    # règles métier
    "orders sans ligne d'article":
        "select count(*) from orders o where not exists "
        "(select 1 from order_items i where i.order_id = o.order_id)",
    "returns : couple (order, product) absent des ventes":
        "select count(*) from returns r where not exists (select 1 from order_items i "
        "where i.order_id = r.order_id and i.product_id = r.product_id)",
    "returns datés avant la commande":
        "select count(*) from returns r join orders o using (order_id) where r.return_ts < o.order_ts",
    "order_items : écart net_amount > 0,02 €":
        "select count(*) from order_items where abs(qty*unit_price*(1-discount_rate) - net_amount) > 0.02",
    "order_items : écart net_amount > 0,10 €":
        "select count(*) from order_items where abs(qty*unit_price*(1-discount_rate) - net_amount) > 0.10",
    "pos_sales : écart net_amount > 0,02 €":
        "select count(*) from pos_sales where abs(qty*unit_price*(1-discount_rate) - net_amount) > 0.02",
    "pos_sales : écart net_amount > 0,10 €":
        "select count(*) from pos_sales where abs(qty*unit_price*(1-discount_rate) - net_amount) > 0.10",
    "pos_sales sans customer_id":
        "select count(*) from pos_sales where customer_id is null",
    "CDC : clients avec plusieurs MAJ":
        "select count(*) from (select customer_id from customer_updates group by 1 having count(*) > 1)",
    "CDC : valeurs distinctes de change_ts":
        "select count(distinct change_ts) from customer_updates",
}

RANGES = {
    "orders.order_ts": "select min(order_ts), max(order_ts) from orders",
    "pos_sales.sale_ts": "select min(sale_ts), max(sale_ts) from pos_sales",
    "clickstream.event_ts": "select min(event_ts), max(event_ts) from clickstream",
    "returns.return_ts": "select min(return_ts), max(return_ts) from returns",
    "gl_entries.posting_date": "select min(posting_date), max(posting_date) from gl_entries",
    "customers.signup_date": "select min(signup_date), max(signup_date) from customers",
}


def main(base: Path) -> None:
    con = duckdb.connect()
    for name, rel in SOURCES.items():
        con.execute(f"create table {name} as select * from read_csv_auto('{base / rel}')")
    for name, rel in JSON_SOURCES.items():
        con.execute(f"create table {name} as select * from read_json_auto('{base / rel}')")

    print("## Volumes et NULL")
    for name in [*SOURCES, *JSON_SOURCES]:
        n = con.sql(f"select count(*) from {name}").fetchone()[0]
        nulls = con.sql(
            f"select column_name, null_percentage from (summarize {name}) where null_percentage > 0"
        ).fetchall()
        print(f"- {name}: {n:,} lignes ; NULL : {nulls or 'aucun'}")

    print("\n## Unicité des clés primaires")
    for name, pk in PRIMARY_KEYS.items():
        dup = con.sql(f"select count(*) - count(distinct {pk}) from {name}").fetchone()[0]
        print(f"- {name}.{pk}: {dup} doublon(s)")

    print("\n## Plages temporelles")
    for label, sql in RANGES.items():
        print(f"- {label}: {con.sql(sql).fetchone()}")

    print("\n## Contrôles")
    for label, sql in CHECKS.items():
        print(f"- {label}: {con.sql(sql).fetchone()[0]:,}")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "data/neoretail_bigdata_pack"))
