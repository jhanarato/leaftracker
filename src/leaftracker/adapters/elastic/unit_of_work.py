from typing import Self, Any

from leaftracker.adapters.elastic.repositories.source_of_stock import ElasticSourceOfStockRepository
from leaftracker.adapters.elastic.repositories.species import ElasticSpeciesRepository
from leaftracker.adapters.elastic.repository import AggregateWriter
from leaftracker.adapters.elastic.repositories.batch import ElasticBatchRepository
from leaftracker.adapters.repository import BatchRepository, SourceOfStockRepository, SpeciesRepository

BATCH_INDEX = "batch"
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
        self._writers: list[AggregateWriter[Any]] = [sources.writer, species.writer, batches.writer]

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self) -> None:
        for writer in self._writers:
            writer.write()

    def rollback(self) -> None:
        for writer in self._writers:
            writer.discard()

    def sources(self) -> SourceOfStockRepository:
        return self._sources

    def species(self) -> SpeciesRepository:
        return self._species

    def batches(self) -> BatchRepository:
        return self._batches
