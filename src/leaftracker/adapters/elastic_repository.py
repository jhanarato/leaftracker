from typing import Protocol

from elasticsearch import NotFoundError

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
        source={"scientific_names": scientific_names}
    )


class DocumentStore(Protocol):
    @property
    def name(self) -> str:
        ...

    def add(self, document: Document) -> str:
        ...

    def get(self, document_id) -> Document:
        ...


class SpeciesRepository:
    def __init__(self, store: DocumentStore):
        self._store = store
        self._added: list[Species] = []

    @property
    def index_name(self) -> str:
        return self._store.name

    def add(self, species: Species):
        self._added.append(species)

    def get(self, reference: str) -> Species | None:
        try:
            document = self._store.get(reference)
        except NotFoundError:
            return None

        return document_to_species(document)

    def added(self) -> list[Species]:
        return self._added

    def commit(self):
        for species in self.added():
            document = species_to_document(species)
            species.reference = self._store.add(document)

        self._added.clear()

    def rollback(self):
        self._added.clear()
