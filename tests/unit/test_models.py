import pytest

from src.models import Product

def test_product_to_dict_serializes_all_fields():
    product = Product(id=1, name="Aceite 1L", price=6.25, stock=10, category="aceites")
    assert product.to_dict() == {
        "id": 1,
        "name": "Aceite 1L",
        "price": 6.25,
        "stock": 10,
        "category": "aceites",
    }

def test_product_invariant_rejects_non_positive_price():
    with pytest.raises(AssertionError):
        Product(id=1, name="X", price=0, stock=1)

def test_product_invariant_rejects_negative_stock():
    with pytest.raises(AssertionError):
        Product(id=1, name="X", price=1.0, stock=-1)
