import pytest

from config.settings import TestingConfig
from src.app import create_app

PRODUCT = {"name": "Arroz 5lb", "price": 4.5, "stock": 20, "category": "granos"}

def _create(client, payload=None):
    return client.post("/api/products", json=payload or PRODUCT)


class TestHealthAndErrors:
    def test_health_endpoint_responds_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.get_json()["status"] == "ok"

    def test_unknown_route_returns_json_404(self, client):
        response = client.get("/api/no-existe")
        assert response.status_code == 404
        assert "error" in response.get_json()

    def test_wrong_method_returns_json_405(self, client):
        response = client.put("/api/products")
        assert response.status_code == 405
        assert "error" in response.get_json()

    def test_security_headers_present(self, client):
        response = client.get("/health")
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"


class TestProductsCrud:
    def test_create_product_returns_201_and_body(self, client):
        response = _create(client)
        assert response.status_code == 201
        body = response.get_json()
        assert body["id"] == 1
        assert body["name"] == "Arroz 5lb"

    def test_create_with_invalid_payload_returns_400(self, client):
        response = _create(client, {"name": "X", "price": -1})
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_create_with_non_json_body_returns_400(self, client):
        response = client.post(
            "/api/products", data="no soy json", content_type="text/plain"
        )
        assert response.status_code == 400

    def test_create_with_unknown_field_returns_400(self, client):
        response = _create(client, {"name": "Arroz 5lb", "prize": 4.5})
        assert response.status_code == 400
        assert "prize" in response.get_json()["error"]

    def test_list_products_returns_created_items(self, client):
        _create(client)
        _create(client, {"name": "Aceite 1L", "price": 6.25, "stock": 8})
        response = client.get("/api/products")
        assert response.status_code == 200
        assert [p["name"] for p in response.get_json()] == ["Arroz 5lb", "Aceite 1L"]

    def test_get_single_product(self, client):
        _create(client)
        response = client.get("/api/products/1")
        assert response.status_code == 200
        assert response.get_json()["name"] == "Arroz 5lb"

    def test_get_missing_product_returns_404(self, client):
        response = client.get("/api/products/999")
        assert response.status_code == 404

    def test_update_product_returns_updated_body(self, client):
        _create(client)
        response = client.put("/api/products/1", json={"price": 5.0})
        assert response.status_code == 200
        assert response.get_json()["price"] == 5.0

    def test_delete_product_returns_204_then_404(self, client):
        _create(client)
        assert client.delete("/api/products/1").status_code == 204
        assert client.get("/api/products/1").status_code == 404


class TestApiKeySecurity:
    class SecuredConfig(TestingConfig):
        API_KEY = "secreto-123"

    @pytest.fixture()
    def secured_client(self):
        return create_app(self.SecuredConfig).test_client()

    def test_write_without_key_returns_401(self, secured_client):
        response = secured_client.post("/api/products", json=PRODUCT)
        assert response.status_code == 401

    def test_write_with_valid_key_succeeds(self, secured_client):
        response = secured_client.post(
            "/api/products", json=PRODUCT, headers={"X-API-Key": "secreto-123"}
        )
        assert response.status_code == 201

    def test_reads_do_not_require_key(self, secured_client):
        assert secured_client.get("/api/products").status_code == 200
