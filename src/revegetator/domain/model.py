from collections import defaultdict
from dataclasses import dataclass
from datetime import date


@dataclass
class Stock:
    species: str
    quantity: int
    size: str


class Batch:
    def __init__(self, reference: str, origin: str, date_received: date):
        self.reference = reference
        self.origin = origin
        self.date_received = date_received
        self._stock_quantites = defaultdict(int)

    def add(self, stock: Stock):
        self._stock_quantites[stock.species] += stock.quantity

    def species(self) -> list[str]:
        return [species for species in self._stock_quantites]

    def quantity(self, species: str) -> int:
        return self._stock_quantites[species]
