import pytest

from leaftracker.adapters.elastic.convert import batch_to_document
from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.domain.model import Batch, BatchType, Stock, StockSize


@pytest.fixture
def batch() -> Batch:
    batch = Batch("source_of_stock-xyz", BatchType.PICKUP, "batch-xyz")
    batch.add(Stock("species-xyz", 20, StockSize.TUBE))
    return batch


@pytest.fixture
def batch_document() -> Document:
    return Document(
        document_id="batch-xyz",
        source={
            "source_reference": "source_of_stock-xyz",
            "batch_type": "pickup",
            "stock": [
                {
                    "species_reference": "species-xyz",
                    "quantity": 20,
                    "size": "tube",
                }
            ]
        }
    )


class TestConvertBatch:
    def test_with_one_stock(self, batch, batch_document):
        assert batch_to_document(batch) == batch_document
