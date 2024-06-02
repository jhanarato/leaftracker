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


def species_to_document(species: Species) -> Document:
    return Document(
        document_id=species.reference,
        source={
            "genus": species.names[0].genus,
            "species": species.names[0].species,
        }
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
        for species in self.added():
            document = species_to_document(species)
            species.reference = self.index.add_document(document)

        self.index.refresh()
        self.clear_added()

    def rollback(self):
        self.clear_added()
