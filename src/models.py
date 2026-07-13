from dataclasses import dataclass, asdict


@dataclass
class Product:
    id: int
    name: str
    price: float
    stock: int
    category: str = "general"

    def __post_init__(self):
        assert self.price > 0, "Invariante violada: price debe ser > 0"
        assert self.stock >= 0, "Invariante violada: stock debe ser >= 0"

    def to_dict(self) -> dict:
        return asdict(self)
