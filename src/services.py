from numbers import Number

from src.exceptions import ValidationError
from src.models import Product
from src.repository import ProductRepository

MAX_NAME_LENGTH = 100
MIN_NAME_LENGTH = 2
MAX_PRICE = 1_000_000
ALLOWED_FIELDS = {"name", "price", "stock", "category"}


def _check_unknown_fields(data: dict) -> None:
    unknown = set(data) - ALLOWED_FIELDS
    if unknown:
        raise ValidationError(f"Campos no reconocidos: {', '.join(sorted(unknown))}")


def _validate_name(name) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("El campo 'name' es obligatorio y debe ser texto")
    name = name.strip()
    if not MIN_NAME_LENGTH <= len(name) <= MAX_NAME_LENGTH:
        raise ValidationError(
            f"'name' debe tener entre {MIN_NAME_LENGTH} y {MAX_NAME_LENGTH} caracteres"
        )
    return name


def _validate_price(price) -> float:
    if isinstance(price, bool) or not isinstance(price, Number):
        raise ValidationError("El campo 'price' debe ser numérico")
    price = float(price)
    if price <= 0:
        raise ValidationError("'price' debe ser mayor que 0")
    if price > MAX_PRICE:
        raise ValidationError(f"'price' no puede superar {MAX_PRICE}")
    return round(price, 2)


def _validate_stock(stock) -> int:
    if isinstance(stock, bool) or not isinstance(stock, int):
        raise ValidationError("El campo 'stock' debe ser un entero")
    if stock < 0:
        raise ValidationError("'stock' no puede ser negativo")
    return stock


def _validate_category(category) -> str:
    if category is None:
        return "general"
    if not isinstance(category, str) or not category.strip():
        raise ValidationError("'category' debe ser texto no vacío")
    return category.strip().lower()


class ProductService:
    def __init__(self, repository: ProductRepository, low_stock_threshold: int = 5):
        assert low_stock_threshold >= 0, "El umbral de stock bajo no puede ser negativo"
        self._repo = repository
        self._low_stock_threshold = low_stock_threshold

    def create_product(self, data: dict) -> Product:
        if not isinstance(data, dict):
            raise ValidationError("El cuerpo de la petición debe ser un objeto JSON")
        _check_unknown_fields(data)
        return self._repo.add(
            name=_validate_name(data.get("name")),
            price=_validate_price(data.get("price")),
            stock=_validate_stock(data.get("stock", 0)),
            category=_validate_category(data.get("category")),
        )

    def get_product(self, product_id: int) -> Product:
        return self._repo.get(product_id)

    def list_products(self) -> list[Product]:
        return self._repo.list_all()

    def update_product(self, product_id: int, data: dict) -> Product:
        if not isinstance(data, dict) or not data:
            raise ValidationError("Debe enviar al menos un campo a actualizar")
        _check_unknown_fields(data)
        product = self._repo.get(product_id)
        if "name" in data:
            product.name = _validate_name(data["name"])
        if "price" in data:
            product.price = _validate_price(data["price"])
        if "stock" in data:
            product.stock = _validate_stock(data["stock"])
        if "category" in data:
            product.category = _validate_category(data["category"])
        return self._repo.save(product)

    def delete_product(self, product_id: int) -> None:
        self._repo.delete(product_id)

    def adjust_stock(self, product_id: int, delta) -> Product:
        if isinstance(delta, bool) or not isinstance(delta, int):
            raise ValidationError("'delta' debe ser un entero")
        if delta == 0:
            raise ValidationError("'delta' no puede ser cero")
        product = self._repo.get(product_id)
        new_stock = product.stock + delta
        if new_stock < 0:
            raise ValidationError(
                f"Stock insuficiente: hay {product.stock} unidades y se pidió retirar {-delta}"
            )
        product.stock = new_stock
        saved = self._repo.save(product)
        assert saved.stock >= 0, "Postcondición violada: stock negativo tras ajuste"
        return saved

    def get_low_stock(self, threshold: int | None = None) -> list[Product]:
        if threshold is None:
            threshold = self._low_stock_threshold
        if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 0:
            raise ValidationError("'threshold' debe ser un entero no negativo")
        return [p for p in self._repo.list_all() if p.stock <= threshold]
