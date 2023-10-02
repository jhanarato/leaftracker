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
        self.stock: dict[str, int] = {}

    def add(self, stock: Stock):
        self.stock[stock.species] = stock.quantity
