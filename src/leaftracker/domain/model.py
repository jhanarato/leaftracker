from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterator, Self


@dataclass(frozen=True)
class WebReference:
    description: str
    site_name: str
    url: str


@dataclass(frozen=True)
class Photo:
    description: str
    name: str


class TaxonName:
    def __init__(self, name: str):
        parts = name.split()
        self._genus = parts[0]
        self._species = parts[1]

        if len(parts) == 3:
            self._subspecies = parts[2]
        else:
            self._subspecies = None

    @property
    def genus(self) -> str:
        return self._genus.capitalize()

    @property
    def species(self) -> str:
        return self._species.lower()

    @property
    def subspecies(self) -> str | None:
        if self._subspecies:
            return self._subspecies.lower()
        return None

    def __str__(self) -> str:
        if self._subspecies:
            return f"{self.genus} {self.species} {self.subspecies}"
        else:
            return f"{self.genus} {self.species}"

    def __repr__(self):
        return f"<TaxonName {self.genus} {self.species}>"

    def __eq__(self, other):
        if not isinstance(other, TaxonName):
            return False
        if other.genus != self.genus:
            return False
        if other.species != self.species:
            return False
        if other.subspecies != self.subspecies:
            return False
        return True


class TaxonHistory:
    def __init__(self):
        self._names = []

    def new_name(self, name: str):
        taxon_name = TaxonName(name)
        self._names.append(taxon_name)

    def current(self) -> TaxonName:
        return self._names[-1]

    def not_current(self) -> list[TaxonName]:
        return self._names[:-1]

    def __iter__(self) -> Iterator[TaxonName]:
        yield from self._names


class Species:
    def __init__(self, reference: str | None = None):
        self.reference = reference
        self.taxon_history = TaxonHistory()
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
