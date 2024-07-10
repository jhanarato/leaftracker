from itertools import count
from typing import Iterator, Self

from leaftracker.adapters.elasticsearch import Document
from leaftracker.adapters.repository import BatchRepository, SourceRepository, SpeciesRepository
from leaftracker.domain.model import Batch, Species, Source


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

    def refresh(self) -> None:
        pass


class FakeDocumentStore:
    def __init__(self, index: str):
        self._index = index
        self._references = references(self._index)
        self._store: dict[str, Document] = dict()

    def index(self) -> str:
        return self._index

    def add(self, document: Document) -> str:
        if document.document_id is None:
            document.document_id = next(self._references)
        self._store[document.document_id] = document
        return document.document_id

    def get(self, document_id) -> Document:
        return self._store[document_id]


class FakeBatchRepository:
    def __init__(self, batches: list[Batch]):
        self._references = references("batch")
        self._batches = set(batches)

    def add(self, batch: Batch) -> str:
        batch.reference = next(self._references)
        self._batches.add(batch)
        return batch.reference

    def get(self, batch_ref: str) -> Batch | None:
        matching = (batch for batch in self._batches
                    if batch.reference == batch_ref)
        return next(matching, None)


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


class FakeSourceRepository:
    def __init__(self, sources: list[Source]):
        self._sources = set(sources)

    def add(self, source: Source) -> str:
        self._sources.add(source)
        return source.name

    def get(self, name: str) -> Source | None:
        matching = (source for source in self._sources
                    if source.name == name)
        return next(matching, None)


class FakeUnitOfWork:
    def __init__(self):
        self._batches = FakeBatchRepository([])
        self._sources = FakeSourceRepository([])
        self._species = FakeSpeciesRepository()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self) -> None:
        self._species.commit()

    def rollback(self) -> None:
        self._species.rollback()

    def batches(self) -> BatchRepository:
        return self._batches

    def sources(self) -> SourceRepository:
        return self._sources

    def species(self) -> SpeciesRepository:
        return self._species

    def set_species(self, repository: FakeSpeciesRepository):
        self._species = repository
