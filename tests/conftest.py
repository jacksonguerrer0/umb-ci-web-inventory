import pytest

from config.settings import TestingConfig
from src.app import create_app
from src.repository import ProductRepository
from src.services import ProductService


@pytest.fixture()
def repo():
    return ProductRepository()


@pytest.fixture()
def service(repo):
    return ProductService(repo, low_stock_threshold=5)


@pytest.fixture()
def app():
    return create_app(TestingConfig)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def sample_product(service):
    return service.create_product(
        {"name": "Arroz 5lb", "price": 4.50, "stock": 20, "category": "granos"}
    )
