from typing import Protocol

from leaftracker.domain.model import Batch, Species, SourceOfStock


class SourceRepository(Protocol):
    def add(self, source: SourceOfStock): ...

    def get(self, reference: str) -> SourceOfStock | None: ...


class SpeciesRepository(Protocol):
    def add(self, species: Species): ...

    def get(self, reference: str) -> Species | None: ...


class BatchRepository(Protocol):
    def add(self, batch: Batch): ...

    def get(self, reference: str) -> Batch | None: ...
