from elasticsearch import NotFoundError

from leaftracker.adapters.indexes import Document, Index
from leaftracker.domain.model import Species, ScientificName


def document_to_species(document: Document) -> Species:
    return Species(
        reference=document.document_id,
        name=ScientificName(
            genus=document.source["genus"],
            species=document.source["species"]
        )
    )


class SpeciesRepository:
    def __init__(self):
        self._mappings = {
            "properties": {
                "genus": {"type": "text"},
                "species": {"type": "text"},
            }
        }

        self.index = Index("species", self._mappings)
        self._queued: list[Species] = []

    def use_test_index(self):
        self.index = Index("test_species", self._mappings)
        self.index.delete()
        self.index.create()

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
