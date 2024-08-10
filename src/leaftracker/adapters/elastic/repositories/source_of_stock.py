from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.adapters.elastic.aggregate_io import DocumentStore, AggregateWriter, AggregateReader
from leaftracker.domain.model import SourceOfStock, SourceType

SOURCE_OF_STOCK_INDEX = "source_of_stock"
SOURCE_OF_STOCK_MAPPINGS = {
    "properties": {
        "current_name": {"type": "text"},
        "source_type": {"type": "keyword"}
    }
}


def source_to_document(source: SourceOfStock) -> Document:
    current_name = source.current_name
    source_type = source.source_type.value

    return Document(
        document_id=source.reference,
        source={
            "current_name": current_name,
            "source_type": source_type,
        }
    )


def document_to_source(document: Document) -> SourceOfStock:
    reference = document.document_id
    current_name = document.source["current_name"]
    source_type = document.source["source_type"]

    return SourceOfStock(current_name, SourceType(source_type), reference)


class ElasticSourceOfStockRepository:
    def __init__(self, store: DocumentStore):
        self.writer = AggregateWriter[SourceOfStock](store, source_to_document)
        self.reader = AggregateReader[SourceOfStock](store, document_to_source)

    def add(self, source: SourceOfStock):
        self.writer.add(source)

    def get(self, reference: str) -> SourceOfStock | None:
        return self.reader.read(reference)
