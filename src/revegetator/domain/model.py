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
        self._stock: list[Stock] = []

    def add(self, stock: Stock):
        self._stock.append(stock)

    def species(self) -> list[str]:
        return [stock.species for stock in self._stock]

    def quantity(self, species: str) -> int:
        return sum(
            [stock.quantity for stock in self._stock
             if stock.species == species]
        )

    def quantity_of_size(self, species: str, size: str) -> int:
        if size:
            return sum(
                [stock.quantity for stock in self._stock
                 if stock.species == species and stock.size == size]
            )

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)


class Species:
    pass
