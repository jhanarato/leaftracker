from dataclasses import dataclass
from datetime import date


@dataclass
class SuppliedStock:
    species: str
    quantity: int
    size: str


class Batch:
    def __init__(self, reference: str, origin: str, date_received: date):
        self.reference = reference
        self.origin = origin
        self.date_received = date_received
        self.stock: list[SuppliedStock] = []

    def add(self, stock: SuppliedStock):
        self.stock.append(stock)
