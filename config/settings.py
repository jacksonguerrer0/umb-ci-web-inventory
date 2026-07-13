import os

class BaseConfig:
    LOW_STOCK_THRESHOLD = int(os.environ.get("LOW_STOCK_THRESHOLD", "5"))
    API_KEY = os.environ.get("API_KEY", "")
    JSON_SORT_KEYS = False

class TestingConfig(BaseConfig):
    TESTING = True
    API_KEY = ""
