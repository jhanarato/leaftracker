from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterator


@dataclass(frozen=True)
class TaxonName:
    genus: str
    species: str
    subspecies: str | None = None
    is_most_recent: bool = True
    year_name_given: str | None = None

    def __str__(self) -> str:
        return f"{self.genus} {self.species}"


@dataclass(frozen=True)
class WebReference:
    description: str
    site_name: str
    url: str


@dataclass(frozen=True)
class Photo:
    description: str
    name: str


class TaxonHistory:
    def __init__(self):
        self._names = []

    def new_name(self, name: str):
        genus, species = name.split()
        taxon_name = TaxonName(genus, species)
        self._names.append(taxon_name)

    def current_name(self) -> TaxonName:
        return self._names[-1]

    def oldest_to_newest(self) -> Iterator[TaxonName]:
        yield from self._names

    def newest_to_oldest(self) -> Iterator[TaxonName]:
        yield from reversed(self._names)


class Species:
    def __init__(self, name: TaxonName, reference: str | None = None):
        self.reference = reference
        self.taxon_history = TaxonHistory()
        self.taxon_names: list[TaxonName] = [name]
        self.common_names: list[str] = []
        self.web_references: list[WebReference] = []
        self.photos: list[Photo] = []

    def __repr__(self):
        return f"<Species {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Species):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)


class StockSize(Enum):
    TUBE = auto()
    POT = auto()


@dataclass(frozen=True)
class Stock:
    species_ref: str
    quantity: int
    size: StockSize


class SourceType(Enum):
    NURSERY = auto()
    PROGRAM = auto()


class Source:
    def __init__(self, name: str, source_type: SourceType):
        self.name = name
        self.source_type = source_type

    def __eq__(self, other):
        if not isinstance(other, Source):
            return False
        return other.name == self.name

    def __hash__(self):
        return hash(self.name)


class BatchType(Enum):
    ORDER = auto()
    DELIVERY = auto()
    PICKUP = auto()


class Batch:
    def __init__(self, source: Source, batch_type: BatchType, reference: str | None = None):
        self.reference = reference
        self.batch_type = batch_type
        self.source = source
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

    def quantity_of_size(self, species_ref: str, size: StockSize) -> int:
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
