from typing import Self

from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository
from leaftracker.adapters.repository import BatchRepository, SourceRepository, SpeciesRepository

SPECIES_INDEX = "species"


SPECIES_MAPPINGS = {
    "properties": {
        "current_scientific_name": {"type": "text"},
        "previous_scientific_names": {"type": "text"},
    }
}

SOURCE_OF_STOCK_INDEX = "source_of_stock"

SOURCE_OF_STOCK_MAPPINGS = {
    "properties": {
        "current_name": {"type": "text"},
        "source_type": {"type": "keyword"}
    }
}


class ElasticUnitOfWork:
    def __init__(self, repository: ElasticSpeciesRepository):
        self._repository = repository

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self) -> None:
        self._repository.commit()

    def rollback(self) -> None:
        self._repository.rollback()

    def batches(self) -> BatchRepository:  # type: ignore
        pass

    def sources(self) -> SourceRepository:  # type: ignore
        pass

    def species(self) -> SpeciesRepository:
        return self._repository
