from typing import Protocol

from leaftracker.domain.model import Batch, Species, Source


class BatchRepository(Protocol):
    def add(self, batch: Batch) -> str: ...

    def get(self, batch_ref: str) -> Batch | None: ...


class SpeciesRepository(Protocol):
    def add(self, species: Species) -> str: ...

    def get(self, reference: str) -> Species | None: ...


class SourceRepository(Protocol):
    def add(self, source: Source) -> str: ...

    def get(self, name: str) -> Source | None: ...
