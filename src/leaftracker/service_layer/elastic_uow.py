from typing import Self, Protocol

from leaftracker.adapters.elasticsearch import DocumentStore
from leaftracker.adapters.elastic_repository import SpeciesRepository
from leaftracker.adapters.repository import BatchRepository, SourceRepository


SPECIES_INDEX = "species"


SPECIES_MAPPINGS = {
    "properties": {
        "scientific_names": {
            "properties": {
                "genus": {"type": "text"},
                "species": {"type": "text"},
            }
        }
    }
}


class Lifecycle(Protocol):
    def create(self) -> None:
        ...

    def refresh(self) -> None:
        ...


class ElasticUnitOfWork:
    def __init__(self, lifecycle: Lifecycle, index_prefix: str = ""):
        self._lifecycle = lifecycle
        self._lifecycle.create()
        store = DocumentStore(index_prefix + SPECIES_INDEX)
        self._species = SpeciesRepository(store)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self) -> None:
        self._species.commit()
        self._lifecycle.refresh()

    def rollback(self) -> None:
        self._species.rollback()

    def batches(self) -> BatchRepository:  # type: ignore
        pass

    def sources(self) -> SourceRepository:  # type: ignore
        pass

    def species(self) -> SpeciesRepository:
        return self._species
