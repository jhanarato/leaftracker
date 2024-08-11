from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.adapters.elastic.aggregate_io import DocumentStore, AggregateWriter, AggregateReader
from leaftracker.domain.model import Batch, BatchType, Stock, StockSize

BATCH_INDEX = "batch"
BATCH_MAPPINGS = {
    "properties": {
        "source_reference": {"type": "keyword"},
        "batch_type": {"type": "keyword"},
        "stock": {
            "properties": {
                "species_reference": {"type": "keyword"},
                "quantity": {"type": "integer"},
                "size": {"type": "keyword"},
            }
        }
    }
}


def stock_for_document(batch: Batch) -> list[dict]:
    return [
        {
            "species_reference": stock.species_reference,
            "quantity": stock.quantity,
            "size": stock.size.value,
        }
        for stock in batch.stock
    ]


def batch_to_document(batch: Batch) -> Document:
    source_reference = batch.source_reference
    batch_type = batch.batch_type.value
    stock = stock_for_document(batch)

    return Document(
        document_id=batch.reference,
        source={
            "source_reference": source_reference,
            "batch_type": batch_type,
            "stock": stock
        }
    )


def document_to_batch(document: Document) -> Batch:
    source_reference = document.source["source_reference"]
    batch_type = document.source["batch_type"]
    batch_reference = document.document_id

    batch = Batch(source_reference, BatchType(batch_type), batch_reference)

    for stock in document.source["stock"]:
        species_reference = stock["species_reference"]
        quantity = stock["quantity"]
        size = StockSize(stock["size"])

        batch.add(Stock(species_reference, quantity, size))

    return batch


class ElasticBatchRepository:
    def __init__(self, store: DocumentStore):
        self.writer = AggregateWriter[Batch](store, batch_to_document)
        self.reader = AggregateReader[Batch](store, document_to_batch)

    def add(self, batch: Batch):
        self.writer.add(batch)

    def get(self, reference: str) -> Batch | None:
        return self.reader.read(reference)
