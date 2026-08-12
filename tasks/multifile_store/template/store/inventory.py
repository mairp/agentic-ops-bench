STOCK = {"apple": 10, "book": 3, "pen": 100}

def in_stock(sku, qty):
    return STOCK.get(sku, 0) >= qty
