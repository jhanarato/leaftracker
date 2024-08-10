import pytest

from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.adapters.elastic.repositories.batch import batch_to_document, document_to_batch
from leaftracker.domain.model import Batch, BatchType, Stock, StockSize


@pytest.fixture
def batch() -> Batch:
    batch = Batch("source-0001", BatchType.PICKUP, "batch-0001")
    batch.add(Stock("species-0001", 20, StockSize.TUBE))
    batch.add(Stock("species-0002", 5, StockSize.POT))
    return batch


@pytest.fixture
def batch_2() -> Batch:
    batch = Batch("source-0001", BatchType.PICKUP, "batch-0002")
    batch.add(Stock("species-0001", 20, StockSize.TUBE))
    batch.add(Stock("species-0002", 5, StockSize.POT))
    return batch


@pytest.fixture
def batch_3() -> Batch:
    batch = Batch("source_of_stock-xyz", BatchType.PICKUP, "batch-xyz")
    batch.add(Stock("species-xyz", 20, StockSize.TUBE))
    return batch


@pytest.fixture
def document_1():
    return Document(
        document_id="batch-0001",
        source={
            "source_reference": "source-0001",
            "batch_type": "pickup",
            "stock": [
                {
                    "species_reference": "species-0001",
                    "quantity": 20,
                    "size": "tube",
                },
                {
                    "species_reference": "species-0002",
                    "quantity": 5,
                    "size": "pot",
                },
            ]
        }
    )


@pytest.fixture
def document_3() -> Document:
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
    def test_with_stock_to_document(self, batch_3, document_3):
        assert batch_to_document(batch_3) == document_3

    def test_from_document_with_stock(self, batch_3, document_3):
        batch = document_to_batch(document_3)
        assert batch.quantity("species-xyz") == 20
