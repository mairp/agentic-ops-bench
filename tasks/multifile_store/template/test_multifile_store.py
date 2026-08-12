import pytest
from store.cart import checkout

def test_no_discount():
    items = [{"sku": "apple", "price": 2.0, "qty": 2, "discount_pct": 0}]
    assert checkout(items) == 4.40          # 4.00 * 1.10

def test_with_discount():
    items = [{"sku": "book", "price": 10.0, "qty": 2, "discount_pct": 10}]
    # 10*2 = 20, less 10% = 18, * 1.10 tax = 19.80
    assert checkout(items) == 19.80

def test_mixed():
    items = [{"sku": "apple", "price": 2.0, "qty": 2, "discount_pct": 0},
             {"sku": "pen", "price": 1.0, "qty": 5, "discount_pct": 20}]
    # 4.00 + (5.00*0.8=4.00) = 8.00 * 1.10 = 8.80
    assert checkout(items) == 8.80

def test_out_of_stock():
    with pytest.raises(ValueError):
        checkout([{"sku": "book", "price": 10.0, "qty": 99, "discount_pct": 0}])
