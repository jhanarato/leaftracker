from typing import Protocol

from leaftracker.adapters.elasticsearch import Document
from leaftracker.domain.model import Species


def document_to_species(document: Document) -> Species:
    names = document.source["scientific_names"]

    current_name = names[-1]
    previous_names = names[:-1]

    species = Species(
        current_name=f"{current_name["genus"]} {current_name["species"]}",
        reference=document.document_id
    )

    for previous_name in previous_names:
        species.taxon_history.add_previous_name(
            f"{previous_name["genus"]} {previous_name["species"]}"
        )

    return species


def species_to_document(species: Species) -> Document:
    scientific_names = [
        {"genus": name.genus, "species": name.species}
        for name in species.taxon_history
    ]

    return Document(
        document_id=species.reference,
        source={
            "scientific_names": scientific_names,
            "current_scientific_name": str(species.taxon_history.current()),
        }
    )


class DocumentStore(Protocol):
    def index(self) -> str:
        ...

    def add(self, document: Document) -> str:
        ...

    def get(self, document_id) -> Document | None:
        ...


class ElasticSpeciesRepository:
    def __init__(self, store: DocumentStore):
        self._store = store
        self._added: list[Species] = []

    def index(self) -> str:
        return self._store.index()

    def add(self, species: Species):
        self._added.append(species)

    def get(self, reference: str) -> Species | None:
        document = self._store.get(reference)
        if document:
            return document_to_species(document)
        return None

    def added(self) -> list[Species]:
        return self._added

    def commit(self):
        for species in self.added():
            document = species_to_document(species)
            species.reference = self._store.add(document)

        self._added.clear()

    def rollback(self):
        self._added.clear()
