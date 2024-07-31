from dataclasses import dataclass
from enum import Enum
from typing import Iterator


@dataclass(frozen=True)
class WebReference:
    description: str
    site_name: str
    url: str


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
    def __init__(self, current_name: str):
        self._current: TaxonName = TaxonName(current_name)
        self._previous: list[TaxonName] = []

    def current(self) -> TaxonName:
        return self._current

    def previous(self) -> Iterator[TaxonName]:
        yield from self._previous

    def new_current_name(self, name: str):
        self._previous.append(self._current)
        self._current = TaxonName(name)

    def add_previous_name(self, name: str):
        self._previous.append(TaxonName(name))

    def __iter__(self) -> Iterator[TaxonName]:
        yield from self._previous

        if self._current:
            yield self._current


class Species:
    def __init__(self, current_name: str, reference: str | None = None):
        self.reference = reference
        self.taxon_history = TaxonHistory(current_name)
        self.common_names: list[str] = []
        self.web_references: list[WebReference] = []

    def __repr__(self):
        return f"<Species {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Species):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)


class StockSize(Enum):
    TUBE = "tube"
    POT = "pot"


@dataclass(frozen=True)
class Stock:
    species_reference: str
    quantity: int
    size: StockSize


class SourceType(Enum):
    NURSERY = "nursery"
    PROGRAM = "program"


class SourceOfStock:
    def __init__(self, current_name: str, source_type: SourceType, reference: str | None = None):
        self.reference = reference
        self.current_name = current_name
        self.source_type = source_type

    def __eq__(self, other):
        if not isinstance(other, SourceOfStock):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)


class BatchType(Enum):
    ORDER = "order"
    DELIVERY = "delivery"
    PICKUP = "pickup"


class Batch:
    def __init__(self, source_reference: str, batch_type: BatchType, reference: str | None = None):
        self.reference = reference
        self.batch_type = batch_type
        self.source_reference = source_reference

        self.stock: list[Stock] = []

    def add(self, stock: Stock):
        self.stock.append(stock)

    def species(self) -> list[str]:
        return [stock.species_reference for stock in self.stock]

    def quantity(self, species_ref: str) -> int:
        return sum(
            [stock.quantity for stock in self.stock
             if stock.species_reference == species_ref]
        )

    def quantity_of_size(self, species_ref: str, size: StockSize) -> int:
        return sum(
            [stock.quantity for stock in self.stock
             if stock.species_reference == species_ref and stock.size == size]
        )

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)
