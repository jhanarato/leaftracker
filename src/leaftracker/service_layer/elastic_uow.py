from typing import Self

from leaftracker.adapters.elastic_repository import SpeciesRepository, SPECIES_INDEX
from leaftracker.adapters.repository import BatchRepository, SourceRepository


class ElasticUnitOfWork:
    def __init__(self, index_prefix: str = ""):
        self._species = SpeciesRepository(index_prefix + SPECIES_INDEX)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self) -> None:
        self._species.commit()

    def rollback(self) -> None:
        self._species.rollback()

    def batches(self) -> BatchRepository:  # type: ignore
        pass

    def sources(self) -> SourceRepository:  # type: ignore
        pass

    def species(self) -> SpeciesRepository:
        return self._species
