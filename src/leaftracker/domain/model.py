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


class MalformedTaxonName(Exception):
    pass


class TaxonName:
    def __init__(self, name: str):
        self._parts = name.split()
        if len(self._parts) not in (2, 3):
            raise MalformedTaxonName(
                f"Taxon must have two or three ranks. Genus, species and optionally subspecies."
            )

    def has_subspecies(self) -> bool:
        return len(self._parts) == 3

    @property
    def genus(self) -> str:
        return self._parts[0].capitalize()

    @property
    def species(self) -> str:
        return self._parts[1].lower()

    @property
    def subspecies(self) -> str | None:
        if self.has_subspecies():
            return self._parts[2].lower()
        return None

    def __str__(self) -> str:
        if self.has_subspecies():
            return f"{self.genus} {self.species} {self.subspecies}"
        else:
            return f"{self.genus} {self.species}"

    def __repr__(self):
        return f"<TaxonName {self.genus} {self.species}>"

    def __eq__(self, other):
        if not isinstance(other, TaxonName):
            return False
        return self._parts == other._parts


class TaxonHistory:
    def __init__(self, current_name: str | None = None):
        self._current = None
        self._previous = []

        if current_name:
            self.new_current_name(current_name)

    def current(self) -> TaxonName | None:
        return self._current

    def previous(self) -> Iterator[TaxonName]:
        yield from self._previous

    def new_current_name(self, name: str):
        if self._current is not None:
            self._previous.append(self._current)

        self._current = TaxonName(name)

    def add_previous_name(self, name: str):
        self._previous.append(TaxonName(name))

    def __iter__(self) -> Iterator[TaxonName]:
        yield from self._previous

        if self._current:
            yield self._current


class Species:
    def __init__(self, reference: str | None = None, current_name: str | None = None):
        self.reference = reference
        self.taxon_history = TaxonHistory(current_name)
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
