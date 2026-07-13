import pytest

from src.exceptions import NotFoundError
from src.models import Product

def test_ids_are_autoincremental(repo):
    first = repo.add(name="Pan", price=1.0, stock=1, category="panadería")
    second = repo.add(name="Leche", price=1.5, stock=2, category="lácteos")
    assert (first.id, second.id) == (1, 2)

def test_save_unknown_product_raises_not_found(repo):
    ghost = Product(id=99, name="Fantasma", price=1.0, stock=1)
    with pytest.raises(NotFoundError):
        repo.save(ghost)

def test_clear_empties_repository_and_resets_ids(repo):
    repo.add(name="Pan", price=1.0, stock=1, category="panadería")
    repo.clear()
    assert repo.list_all() == []
    assert repo.add(name="Leche", price=1.5, stock=2, category="lácteos").id == 1
