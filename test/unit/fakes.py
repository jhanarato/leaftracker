from itertools import count
from typing import Iterator, Self

from leaftracker.adapters.elasticsearch import Document
from leaftracker.adapters.repository import BatchRepository, SourceOfStockRepository, SpeciesRepository
from leaftracker.domain.model import Batch, Species, SourceOfStock


def references(prefix: str) -> Iterator[str]:
    for i in count(start=1):
        yield f"{prefix}-{i:04}"


class FakeLifecycle:
    def __init__(self, exists: bool):
        self._exists = exists

    def create(self) -> None:
        self._exists = True

    def delete(self) -> None:
        self._exists = False

    def exists(self) -> bool:
        return self._exists


class FakeDocumentStore:
    def __init__(self, index: str):
        self._index = index
        self._references = references(self._index)
        self._documents: dict[str, Document] = dict()

    def index(self) -> str:
        return self._index

    def add(self, document: Document) -> str:
        if document.document_id is None:
            document.document_id = next(self._references)
        self._documents[document.document_id] = document
        return document.document_id

    def get(self, document_id) -> Document | None:
        return self._documents.get(document_id)

    def ids(self) -> list[str]:
        return [document.document_id for document in self._documents.values()]


class FakeBatchRepository:
    def __init__(self):
        self._added = set()
        self._committed = dict()
        self.references = references("batch")

    def add(self, batch: Batch):
        self._added.add(batch)

    def get(self, reference: str) -> Batch | None:
        return self._committed.get(reference)

    def commit(self):
        for batch in self._added:
            batch.reference = next(self.references)
            self._committed[batch.reference] = batch

    def rollback(self):
        self._added.clear()


class FakeSpeciesRepository:
    def __init__(self):
        self._added = set()
        self._committed = dict()
        self.references = references("species")

    def add(self, species: Species):
        self._added.add(species)

    def get(self, reference: str) -> Species | None:
        return self._committed.get(reference)

    def commit(self):
        for species in self._added:
            species.reference = next(self.references)
            self._committed[species.reference] = species

    def rollback(self):
        self._added.clear()


class FakeSourceOfStockRepository:
    def __init__(self):
        self._added = set()
        self._committed = dict()
        self.references = references("source")

    def add(self, source: SourceOfStock):
        self._added.add(source)

    def get(self, reference: str) -> SourceOfStock | None:
        return self._committed.get(reference)

    def commit(self):
        for source in self._added:
            source.reference = next(self.references)
            self._committed[source.reference] = source

    def rollback(self):
        self._added.clear()


class FakeUnitOfWork:
    def __init__(self):
        self._batches = FakeBatchRepository()
        self._sources = FakeSourceOfStockRepository()
        self._species = FakeSpeciesRepository()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self) -> None:
        self._species.commit()
        self._sources.commit()
        self._batches.commit()

    def rollback(self) -> None:
        self._species.rollback()
        self._sources.rollback()
        self._batches.rollback()

    def batches(self) -> BatchRepository:
        return self._batches

    def sources(self) -> SourceOfStockRepository:
        return self._sources

    def species(self) -> SpeciesRepository:
        return self._species

    def set_species(self, repository: FakeSpeciesRepository):
        self._species = repository
