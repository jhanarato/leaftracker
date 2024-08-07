from typing import Self

from leaftracker.adapters.elastic.repository import ElasticSpeciesRepository, ElasticBatchRepository, \
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
        self._sources = sources
        self._species = species
        self._batches = batches

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self) -> None:
        self._sources.commit()
        self._species.commit()
        self._batches.commit()

    def rollback(self) -> None:
        self._sources.rollback()
        self._species.rollback()
        self._batches.rollback()

    def sources(self) -> SourceOfStockRepository:
        return self._sources

    def species(self) -> SpeciesRepository:
        return self._species

    def batches(self) -> BatchRepository:
        return self._batches