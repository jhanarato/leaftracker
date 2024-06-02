from elasticsearch import NotFoundError

from leaftracker.adapters.elastic_index import Document, Index
from leaftracker.domain.model import Species, ScientificName

SPECIES_INDEX = "species"

SPECIES_MAPPINGS = {
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
    def __init__(self, index_name: str = SPECIES_INDEX):
        self.index = Index(index_name, SPECIES_MAPPINGS)
        self.index.create()

        self._added: list[Species] = []

    def add(self, species: Species):
        self._added.append(species)

    def get(self, reference: str) -> Species | None:
        try:
            document = self.index.get_document(reference)
        except NotFoundError:
            return None

        return document_to_species(document)

    def added(self) -> list[Species]:
        return self._added

    def clear_added(self) -> None:
        self._added.clear()

    def commit(self):
        pass

    def rollback(self):
        self.clear_added()
