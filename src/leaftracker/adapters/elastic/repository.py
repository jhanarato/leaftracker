from collections.abc import Callable, Iterator
from typing import Protocol

from leaftracker.adapters.elastic.convert import(
    batch_to_document, document_to_batch,
)

from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.domain.model import Species, Batch


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
        aggregate = None
        document = self._store.get(reference)
        if document:
            aggregate = self._to_aggregate(document)
        return aggregate



class ElasticBatchRepository:
    def __init__(self, store: DocumentStore):
        self.writer = AggregateWriter[Batch](store, batch_to_document)
        self.reader = AggregateReader[Batch](store, document_to_batch)

    def add(self, batch: Batch):
        self.writer.add(batch)

    def get(self, reference: str) -> Batch | None:
        return self.reader.read(reference)
