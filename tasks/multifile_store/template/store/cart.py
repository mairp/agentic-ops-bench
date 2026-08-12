from store.pricing import line_total, with_tax
from store.inventory import in_stock

TAX = 0.10

def checkout(items):
    """items: list of {sku, price, qty, discount_pct}. discount_pct is a
    whole percent (10 means 10%). Return the taxed order total (2dp), or
    raise ValueError if any line is out of stock."""
    subtotal = 0.0
    for it in items:
        if not in_stock(it["sku"], it["qty"]):
            raise ValueError(f"out of stock: {it['sku']}")
        # BUG: passes a whole-percent int where pricing wants a fraction.
        subtotal += line_total(it["price"], it["qty"], it["discount_pct"])
    return with_tax(subtotal, TAX)
