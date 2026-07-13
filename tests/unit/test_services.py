import pytest

from src.exceptions import NotFoundError, ValidationError

class TestCreateProduct:
    def test_creates_product_with_valid_data(self, service):
        product = service.create_product(
            {"name": "Café molido", "price": 8.99, "stock": 12, "category": "Bebidas"}
        )
        assert product.id == 1
        assert product.name == "Café molido"
        assert product.price == 8.99
        assert product.stock == 12
        assert product.category == "bebidas"

    def test_stock_defaults_to_zero(self, service):
        product = service.create_product({"name": "Azúcar", "price": 2.0})
        assert product.stock == 0

    def test_price_is_rounded_to_two_decimals(self, service):
        product = service.create_product({"name": "Azúcar", "price": 4.999})
        assert product.price == 5.0

    def test_name_is_trimmed(self, service):
        product = service.create_product({"name": "  Café molido  ", "price": 8.99})
        assert product.name == "Café molido"

    def test_name_boundary_lengths_are_accepted(self, service):
        assert service.create_product({"name": "Ají", "price": 1.0}).name == "Ají"
        long_name = "x" * 100
        assert service.create_product({"name": long_name, "price": 1.0}).name == long_name

    def test_name_over_max_length_is_rejected(self, service):
        with pytest.raises(ValidationError):
            service.create_product({"name": "x" * 101, "price": 1.0})

    def test_price_at_maximum_is_accepted(self, service):
        product = service.create_product({"name": "Maquinaria", "price": 1_000_000})
        assert product.price == 1_000_000

    def test_name_is_required(self, service):
        with pytest.raises(ValidationError):
            service.create_product({"price": 1.0, "stock": 1})

    def test_name_too_short_is_rejected(self, service):
        with pytest.raises(ValidationError):
            service.create_product({"name": "A", "price": 1.0})

    def test_whitespace_name_is_rejected(self, service):
        with pytest.raises(ValidationError):
            service.create_product({"name": "   ", "price": 1.0})

    def test_price_must_be_numeric(self, service):
        with pytest.raises(ValidationError):
            service.create_product({"name": "Harina", "price": "gratis"})

    def test_price_zero_or_negative_is_rejected(self, service):
        for bad_price in (0, -5):
            with pytest.raises(ValidationError):
                service.create_product({"name": "Harina", "price": bad_price})

    def test_price_above_maximum_is_rejected(self, service):
        with pytest.raises(ValidationError):
            service.create_product({"name": "Harina", "price": 2_000_000})

    def test_negative_stock_is_rejected(self, service):
        with pytest.raises(ValidationError):
            service.create_product({"name": "Harina", "price": 1.0, "stock": -3})

    def test_boolean_stock_is_rejected(self, service):
        with pytest.raises(ValidationError):
            service.create_product({"name": "Harina", "price": 1.0, "stock": True})

    def test_boolean_price_is_rejected(self, service):
        with pytest.raises(ValidationError):
            service.create_product({"name": "Harina", "price": True})

    def test_unknown_fields_are_rejected(self, service):
        with pytest.raises(ValidationError, match="prize"):
            service.create_product({"name": "Harina", "prize": 2.0})

    def test_invalid_category_is_rejected(self, service):
        for bad_category in ("", "   ", 123):
            with pytest.raises(ValidationError):
                service.create_product({"name": "Harina", "price": 1.0, "category": bad_category})

    def test_non_dict_body_is_rejected(self, service):
        with pytest.raises(ValidationError):
            service.create_product(["no", "soy", "objeto"])


class TestReadUpdateDelete:
    def test_get_product_returns_existing(self, service, sample_product):
        assert service.get_product(sample_product.id).name == "Arroz 5lb"

    def test_get_missing_product_raises_not_found(self, service):
        with pytest.raises(NotFoundError):
            service.get_product(999)

    def test_list_products_returns_all_ordered(self, service):
        service.create_product({"name": "Pan", "price": 1.0})
        service.create_product({"name": "Leche", "price": 1.5})
        names = [p.name for p in service.list_products()]
        assert names == ["Pan", "Leche"]

    def test_partial_update_changes_only_sent_fields(self, service, sample_product):
        updated = service.update_product(sample_product.id, {"price": 5.25})
        assert updated.price == 5.25
        assert updated.name == "Arroz 5lb"
        assert updated.stock == 20

    def test_update_multiple_fields_at_once(self, service, sample_product):
        updated = service.update_product(
            sample_product.id,
            {"name": "Arroz 10lb", "stock": 40, "category": "Granos Premium"},
        )
        assert updated.name == "Arroz 10lb"
        assert updated.stock == 40
        assert updated.category == "granos premium"

    def test_update_with_empty_body_is_rejected(self, service, sample_product):
        with pytest.raises(ValidationError):
            service.update_product(sample_product.id, {})

    def test_update_with_invalid_price_is_rejected(self, service, sample_product):
        with pytest.raises(ValidationError):
            service.update_product(sample_product.id, {"price": -1})

    def test_update_with_unknown_field_is_rejected(self, service, sample_product):
        with pytest.raises(ValidationError, match="descripcion"):
            service.update_product(sample_product.id, {"descripcion": "no existe"})
        assert service.get_product(sample_product.id).name == "Arroz 5lb"

    def test_update_missing_product_raises_not_found(self, service):
        with pytest.raises(NotFoundError):
            service.update_product(999, {"price": 2.0})

    def test_delete_removes_product(self, service, sample_product):
        service.delete_product(sample_product.id)
        with pytest.raises(NotFoundError):
            service.get_product(sample_product.id)

    def test_delete_missing_product_raises_not_found(self, service):
        with pytest.raises(NotFoundError):
            service.delete_product(999)
