from typing import Protocol

from leaftracker.adapters.elasticsearch import Document
from leaftracker.domain.model import Species, Source


class DocumentStore(Protocol):
    def index(self) -> str:
        ...

    def add(self, document: Document) -> str:
        ...

    def get(self, document_id) -> Document | None:
        ...


def document_to_species(document: Document) -> Species:
    current_name = document.source["current_scientific_name"]
    previous_names = document.source["previous_scientific_names"]

    species = Species(
        current_name=current_name,
        reference=document.document_id
    )

    for previous_name in previous_names:
        species.taxon_history.add_previous_name(previous_name)

    return species


def species_to_document(species: Species) -> Document:
    current_scientific_name = str(species.taxon_history.current())
    other_scientific_names = [str(name) for name in species.taxon_history.previous()]

    return Document(
        document_id=species.reference,
        source={
            "current_scientific_name": current_scientific_name,
            "previous_scientific_names": other_scientific_names,
        }
    )


class ElasticSpeciesRepository:
    def __init__(self, store: DocumentStore):
        self._store = store
        self._added: list[Species] = []

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


def source_to_document(source: Source) -> Document:
    current_name = source.name
    source_type = source.source_type.value

    return Document(
        document_id=current_name,
        source={
            "current_name": current_name,
            "source_type": source_type,
        }
    )


class ElasticSourceRepository:
    def __init__(self, store: DocumentStore):
        self._store = store
        self._added: list[Source] = []

    def add(self, source: Source):
        self._added.append(source)

    def added(self) -> list[Source]:
        return self._added

    def commit(self):
        for source in self.added():
            document = source_to_document(source)
            source.reference = self._store.add(document)

        self._added.clear()

    def rollback(self):
        self._added.clear()
