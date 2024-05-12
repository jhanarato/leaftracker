from typing import Self

from leaftracker.adapters.repository import BatchRepository, SourceRepository
from leaftracker.adapters.elastic_repository import SpeciesRepository


class ElasticUnitOfWork:
    def __enter__(self) -> Self:
        pass

    def __exit__(self, *args):
        pass

    def commit(self) -> None:
        pass

    def committed(self) -> bool:
        pass

    def rollback(self) -> None:
        pass

    def batches(self) -> BatchRepository:
        pass

    def sources(self) -> SourceRepository:
        pass

    def species(self) -> SpeciesRepository:
        return SpeciesRepository()
