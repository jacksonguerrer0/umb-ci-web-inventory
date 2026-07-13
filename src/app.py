from flask import Flask, jsonify

from config.settings import BaseConfig
from src.exceptions import ApiError
from src.repository import ProductRepository
from src.routes import api
from src.services import ProductService


def create_app(config_object=BaseConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    repository = ProductRepository()
    service = ProductService(
        repository, low_stock_threshold=app.config["LOW_STOCK_THRESHOLD"]
    )
    app.extensions["product_service"] = service

    app.register_blueprint(api)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "inventory-api"}), 200

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return jsonify({"error": "Método no permitido"}), 405

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    return app


if __name__ == "__main__":  # pragma: no cover
    create_app().run(host="127.0.0.1", port=5000, debug=False)
