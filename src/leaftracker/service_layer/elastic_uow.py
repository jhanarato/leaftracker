from typing import Self

from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository, ElasticBatchRepository, \
    ElasticSourceOfStockRepository
from leaftracker.adapters.repository import BatchRepository, SourceOfStockRepository, SpeciesRepository

SPECIES_INDEX = "species"
SOURCE_OF_STOCK_INDEX = "source_of_stock"
BATCH_INDEX = "batch"

SPECIES_MAPPINGS = {
    "properties": {
        "current_scientific_name": {"type": "text"},
        "previous_scientific_names": {"type": "text"},
    }
}


SOURCE_OF_STOCK_MAPPINGS = {
    "properties": {
        "current_name": {"type": "text"},
        "source_type": {"type": "keyword"}
    }
}


BATCH_MAPPINGS = {
    "properties": {
        "source_reference": {"type": "keyword"},
        "batch_type": {"type": "keyword"},
        "stock": {
            "properties": {
                "species_reference": {"type": "keyword"},
                "quantity": {"type": "integer"},
                "size": {"type": "keyword"},
            }
        }
    }
}


class ElasticUnitOfWork:
    def __init__(self,
                 sources: ElasticSourceOfStockRepository,
                 species: ElasticSpeciesRepository,
                 batches: ElasticBatchRepository):
        self._species = species

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

    def sources(self) -> SourceOfStockRepository:  # type: ignore
        pass

    def species(self) -> SpeciesRepository:
        return self._species
