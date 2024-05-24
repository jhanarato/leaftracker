from typing import Self

from leaftracker.adapters.repository import BatchRepository, SourceRepository
from leaftracker.adapters.elastic_repository import SpeciesRepository
from leaftracker.adapters.elastic import Document
from leaftracker.domain.model import Species


def species_to_document(species: Species) -> Document:
    return Document(
        document_id=species.reference,
        source={
            "genus": species.names[0].genus,
            "species": species.names[0].species,
        }
    )


class ElasticUnitOfWork:
    def __init__(self, use_test_indexes: bool = False):
        if use_test_indexes:
            self._species = SpeciesRepository(index_name="test_species")
            self._species.index.delete()
            self._species.index.create()
        else:
            self._species = SpeciesRepository()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self) -> None:
        for species in self._species.queued():
            document = species_to_document(species)
            species.reference = self._species.index.add_document(document)

        self._species.index.refresh()
        self._species.clear_queue()

    def rollback(self) -> None:
        self._species.clear_queue()

    def batches(self) -> BatchRepository:  # type: ignore
        pass

    def sources(self) -> SourceRepository:  # type: ignore
        pass

    def species(self) -> SpeciesRepository:
        return self._species
