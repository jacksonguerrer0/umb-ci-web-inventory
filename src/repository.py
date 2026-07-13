from src.exceptions import NotFoundError
from src.models import Product


class ProductRepository:
    def __init__(self):
        self._items: dict[int, Product] = {}
        self._next_id = 1

    def add(self, name: str, price: float, stock: int, category: str) -> Product:
        product = Product(
            id=self._next_id, name=name, price=price, stock=stock, category=category
        )
        self._items[product.id] = product
        self._next_id += 1
        return product

    def get(self, product_id: int) -> Product:
        product = self._items.get(product_id)
        if product is None:
            raise NotFoundError(f"Producto {product_id} no existe")
        return product

    def list_all(self) -> list[Product]:
        return sorted(self._items.values(), key=lambda p: p.id)

    def save(self, product: Product) -> Product:
        if product.id not in self._items:
            raise NotFoundError(f"Producto {product.id} no existe")
        self._items[product.id] = product
        return product

    def delete(self, product_id: int) -> None:
        if product_id not in self._items:
            raise NotFoundError(f"Producto {product_id} no existe")
        del self._items[product_id]

    def clear(self) -> None:
        self._items.clear()
        self._next_id = 1
