from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class ScientificName:
    genus: str
    species: str
    subspecies: Optional[str]
    year_name_given: Optional[int]
    is_most_recently_used: bool


@dataclass(frozen=True)
class WebReference:
    reference: str
    site_name: str
    url: str


class Species:
    def __init__(self, reference: str, name: ScientificName):
        self.reference = reference
        self.names: list[ScientificName] = [name]
        self.common_names: list[str] = []
        self.web_references: list[WebReference] = []


@dataclass(frozen=True)
class Stock:
    species_ref: str
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
        return [stock.species_ref for stock in self._stock]

    def quantity(self, species: str) -> int:
        return sum(
            [stock.quantity for stock in self._stock
             if stock.species_ref == species]
        )

    def quantity_of_size(self, species: str, size: str) -> int:
        if size:
            return sum(
                [stock.quantity for stock in self._stock
                 if stock.species_ref == species and stock.size == size]
            )

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)
