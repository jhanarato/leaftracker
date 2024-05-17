from typing import Self

from leaftracker.adapters.repository import BatchRepository, SourceRepository
from leaftracker.adapters.elastic_repository import SpeciesRepository, Document
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
    def __init__(self):
        self._species = SpeciesRepository()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args):
        pass

    def commit(self) -> None:
        species = self._species.queued()[0]
        document = species_to_document(species)
        species.reference = self._species.index.add_document(document.source, document.document_id)
        self._species.index.refresh()

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
