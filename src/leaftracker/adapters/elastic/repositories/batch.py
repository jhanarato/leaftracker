from leaftracker.adapters.elastic.convert import batch_to_document, document_to_batch
from leaftracker.adapters.elastic.repository import DocumentStore, AggregateWriter, AggregateReader
from leaftracker.domain.model import Batch


class ElasticBatchRepository:
    def __init__(self, store: DocumentStore):
        self.writer = AggregateWriter[Batch](store, batch_to_document)
        self.reader = AggregateReader[Batch](store, document_to_batch)

    def add(self, batch: Batch):
        self.writer.add(batch)

    def get(self, reference: str) -> Batch | None:
        return self.reader.read(reference)
