from leaftracker.adapters.elastic.convert import source_to_document, document_to_source
from leaftracker.adapters.elastic.repository import DocumentStore, AggregateWriter, AggregateReader
from leaftracker.domain.model import SourceOfStock


SOURCE_OF_STOCK_INDEX = "source_of_stock"
SOURCE_OF_STOCK_MAPPINGS = {
    "properties": {
        "current_name": {"type": "text"},
        "source_type": {"type": "keyword"}
    }
}


class ElasticSourceOfStockRepository:
    def __init__(self, store: DocumentStore):
        self.writer = AggregateWriter[SourceOfStock](store, source_to_document)
        self.reader = AggregateReader[SourceOfStock](store, document_to_source)

    def add(self, source: SourceOfStock):
        self.writer.add(source)

    def get(self, reference: str) -> SourceOfStock | None:
        return self.reader.read(reference)
