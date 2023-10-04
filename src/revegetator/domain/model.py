from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ScientificName:
    genus: str
    species: str
    subspecies: str | None
    year_name_given: str | None
    is_most_recent: bool


@dataclass(frozen=True)
class WebReference:
    description: str
    site_name: str
    url: str


@dataclass(frozen=True)
class Photo:
    description: str
    name: str


class Species:
    def __init__(self, reference: str, name: ScientificName):
        self.reference = reference
        self.names: list[ScientificName] = [name]
        self.common_names: list[str] = []
        self.web_references: list[WebReference] = []
        self.photos: list[Photo] = []


@dataclass(frozen=True)
class Stock:
    species_ref: str
    quantity: int
    size: str


class Source:
    def __init__(self, name: str):
        self.name = name


class Batch:
    def __init__(self, source: Source, date_received: date, reference: str | None = None):
        self.reference = reference
        self.source = source
        self.date_received = date_received
        self._stock: list[Stock] = []

    def add(self, stock: Stock):
        self._stock.append(stock)

    def species(self) -> list[str]:
        return [stock.species_ref for stock in self._stock]

    def quantity(self, species_ref: str) -> int:
        return sum(
            [stock.quantity for stock in self._stock
             if stock.species_ref == species_ref]
        )

    def quantity_of_size(self, species_ref: str, size: str) -> int:
        if size:
            return sum(
                [stock.quantity for stock in self._stock
                 if stock.species_ref == species_ref and stock.size == size]
            )

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)
