from elasticsearch import NotFoundError

from leaftracker.adapters.elastic_index import Document, Index
from leaftracker.domain.model import Species, ScientificName

SPECIES_INDEX = "species"

SPECIES_MAPPING = {
    "properties": {
        "genus": {"type": "text"},
        "species": {"type": "text"},
    }
}


def document_to_species(document: Document) -> Species:
    return Species(
        reference=document.document_id,
        name=ScientificName(
            genus=document.source["genus"],
            species=document.source["species"]
        )
    )


class SpeciesRepository:
    def __init__(self, index: Index = Index(SPECIES_INDEX, SPECIES_MAPPING)):
        self.index = index
        self.index.create()
        self._queued: list[Species] = []

    def add(self, species: Species):
        self._queued.append(species)

    def get(self, reference: str) -> Species | None:
        try:
            document = self.index.get_document(reference)
        except NotFoundError:
            return None

        return document_to_species(document)

    def queued(self) -> list[Species]:
        return self._queued

    def clear_queue(self) -> None:
        self._queued.clear()
