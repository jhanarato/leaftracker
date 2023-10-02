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
        self.quantity = defaultdict(int)

    def add(self, stock: Stock):
        self.quantity[stock.species] += stock.quantity
