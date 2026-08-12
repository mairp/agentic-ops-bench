def line_total(price, qty, discount):
    """Total for one line. `discount` is a FRACTION in [0,1] (0.10 == 10%)."""
    return price * qty * (1 - discount)

def with_tax(subtotal, tax_rate):
    """Apply tax_rate (fraction), rounded to cents."""
    return round(subtotal * (1 + tax_rate), 2)
