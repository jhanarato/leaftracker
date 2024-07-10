from typing import Self, Protocol

from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository
from leaftracker.adapters.elasticsearch import Document
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
    def __init__(self, lifecycle: Lifecycle, repository: ElasticSpeciesRepository):
        self._repository = repository
        self._lifecycle = lifecycle
        self._lifecycle.create()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self) -> None:
        self._repository.commit()
        self._lifecycle.refresh()

    def rollback(self) -> None:
        self._repository.rollback()

    def batches(self) -> BatchRepository:  # type: ignore
        pass

    def sources(self) -> SourceRepository:  # type: ignore
        pass

    def species(self) -> ElasticSpeciesRepository:
        return self._repository
