from typing import Self

from leaftracker.adapters.repository import BatchRepository, SourceRepository
from leaftracker.adapters.elastic_repository import SpeciesRepository


class ElasticUnitOfWork:
    def __init__(self):
        self._species = SpeciesRepository()

    def __enter__(self) -> Self:  # type: ignore
        pass

    def __exit__(self, *args):
        pass

    def commit(self) -> None:
        pass

    def committed(self) -> bool:  # type: ignore
        pass

    def rollback(self) -> None:
        pass

    def batches(self) -> BatchRepository:  # type: ignore
        pass

    def sources(self) -> SourceRepository:  # type: ignore
        pass

    def species(self) -> SpeciesRepository:
        return self._species
