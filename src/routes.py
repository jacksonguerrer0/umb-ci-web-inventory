from flask import Blueprint, current_app, jsonify, request

from src.exceptions import AuthError, ValidationError

api = Blueprint("api", __name__, url_prefix="/api")

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _service():
    return current_app.extensions["product_service"]


@api.before_request
def require_api_key():
    configured_key = current_app.config.get("API_KEY", "")
    if configured_key and request.method in WRITE_METHODS:
        if request.headers.get("X-API-Key") != configured_key:
            raise AuthError("Falta o es inválida la cabecera X-API-Key")


def _json_body() -> dict:
    data = request.get_json(silent=True)
    if data is None:
        raise ValidationError("El cuerpo debe ser JSON válido (Content-Type: application/json)")
    return data


@api.get("/products")
def list_products():
    products = _service().list_products()
    return jsonify([p.to_dict() for p in products]), 200


@api.post("/products")
def create_product():
    product = _service().create_product(_json_body())
    return jsonify(product.to_dict()), 201


@api.get("/products/<int:product_id>")
def get_product(product_id: int):
    return jsonify(_service().get_product(product_id).to_dict()), 200


@api.put("/products/<int:product_id>")
def update_product(product_id: int):
    product = _service().update_product(product_id, _json_body())
    return jsonify(product.to_dict()), 200


@api.delete("/products/<int:product_id>")
def delete_product(product_id: int):
    _service().delete_product(product_id)
    return "", 204
