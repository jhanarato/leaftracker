from typing import Protocol

from leaftracker.domain.model import Batch, Species, SourceOfStock


class BatchRepository(Protocol):
    def add(self, batch: Batch) -> str: ...

    def get(self, batch_ref: str) -> Batch | None: ...


class SpeciesRepository(Protocol):
    def add(self, species: Species): ...

    def get(self, reference: str) -> Species | None: ...


class SourceRepository(Protocol):
    def add(self, source: SourceOfStock) -> str: ...

    def get(self, name: str) -> SourceOfStock | None: ...
