from typing import Protocol

from revegetator.domain.model import Batch, Species


class BatchRepository(Protocol):
    def add(self, batch: Batch) -> str: ...

    def get(self, batch_ref: str) -> Batch: ...


class SpeciesRepository(Protocol):
    def add(self, species: Species) -> str: ...

    def get(self, species_ref: str) -> Species: ...
