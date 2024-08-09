from collections.abc import Callable, Iterator
from typing import Protocol

from leaftracker.adapters.elastic.convert import(
    document_to_species, species_to_document,
    source_to_document, document_to_source,
    batch_to_document, document_to_batch,
)

from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.domain.model import Species, SourceOfStock, Batch


class DocumentStore(Protocol):
    def index(self) -> str:
        ...

    def add(self, document: Document) -> str:
        ...

    def get(self, document_id) -> Document | None:
        ...


class AggregateWriter[Aggregate]:
    def __init__(self, store: DocumentStore, to_document: Callable[[Aggregate], Document]):
        self._store = store
        self._added: list[Aggregate] = []
        self._to_document = to_document

    def add(self, aggregate: Aggregate) -> None:
        self._added.append(aggregate)

    def added(self) -> Iterator:
        yield from self._added

    def discard(self) -> None:
        self._added.clear()

    def write(self) -> None:
        for aggregate in self.added():
            document = self._to_document(aggregate)
            reference = self._store.add(document)
            aggregate.reference = reference

        self.discard()


class AggregateReader[Aggregate]:
    def __init__(self, store: DocumentStore, to_aggregate: Callable[[Document], Aggregate]):
        self._store = store
        self._to_aggregate = to_aggregate

    def read(self, reference: str) -> Aggregate | None:
        document = self._store.get(reference)
        if document:
            return self._to_aggregate(document)
        return None


class ElasticSpeciesRepository:
    def __init__(self, store: DocumentStore):
        self._store = store
        self.writer = AggregateWriter[Species](store, species_to_document)

    def add(self, species: Species):
        self.writer.add(species)

    def get(self, reference: str) -> Species | None:
        document = self._store.get(reference)
        if document:
            return document_to_species(document)
        return None

    def added(self) -> list[Species]:
        return list(self.writer.added())

    def commit(self):
        self.writer.write()

    def rollback(self):
        self.writer.discard()


class ElasticSourceOfStockRepository:
    def __init__(self, store: DocumentStore):
        self._store = store
        self.writer = AggregateWriter[SourceOfStock](store, source_to_document)

    def add(self, source: SourceOfStock):
        self.writer.add(source)

    def get(self, reference: str) -> SourceOfStock | None:
        document = self._store.get(reference)
        if document:
            return document_to_source(document)
        return None

    def added(self) -> list[SourceOfStock]:
        return list(self.writer.added())

    def commit(self):
        self.writer.write()

    def rollback(self):
        self.writer.discard()


class ElasticBatchRepository:
    def __init__(self, store: DocumentStore):
        self._store = store
        self.writer = AggregateWriter[Batch](store, batch_to_document)

    def add(self, batch: Batch):
        self.writer.add(batch)

    def get(self, reference: str) -> Batch | None:
        document = self._store.get(reference)
        if document:
            return document_to_batch(document)
        return None

    def added(self) -> list[Batch]:
        return list(self.writer.added())

    def commit(self):
        self.writer.write()

    def rollback(self):
        self.writer.discard()
