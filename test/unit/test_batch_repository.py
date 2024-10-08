import pytest

from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.domain.model import Batch, BatchType, Stock, StockSize


@pytest.fixture
def batch_with_none() -> Batch:
    return Batch("source-0001", BatchType.PICKUP, "batch-0001")


@pytest.fixture
def document_with_none() -> Document:
    return Document(
        document_id="batch-0001",
        source={
            "source_reference": "source-0001",
            "batch_type": "pickup",
            "stock": []
        }
    )


@pytest.fixture
def batch_with_one() -> Batch:
    batch = Batch("source-0001", BatchType.PICKUP, "batch-0001")
    batch.add(Stock("species-0001", 20, StockSize.TUBE))
    return batch


@pytest.fixture
def document_with_one():
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
            ]
        }
    )


@pytest.fixture
def batch_with_two() -> Batch:
    batch = Batch("source-0001", BatchType.PICKUP, "batch-0001")
    batch.add(Stock("species-0001", 20, StockSize.TUBE))
    batch.add(Stock("species-0002", 5, StockSize.POT))
    return batch


@pytest.fixture
def document_with_two() -> Document:
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


class TestElasticBatchRepository:
    def test_add_batch_with_no_stock(self, uow, batch_store, batch_with_none, document_with_none):
        with uow:
            uow.batches().add(batch_with_none)
            uow.commit()

        stored = batch_store.get(document_with_none.document_id)

        assert stored == document_with_none

    def test_add_batch_with_one_stock(self, uow, batch_store, batch_with_one, document_with_one):
        with uow:
            uow.batches().add(batch_with_one)
            uow.commit()

        stored = batch_store.get(document_with_one.document_id)

        assert stored == document_with_one

    def test_add_batch_with_two_stock(self, uow, batch_store, batch_with_two, document_with_two):
        with uow:
            uow.batches().add(batch_with_two)
            uow.commit()

        stored = batch_store.get(document_with_two.document_id)

        assert stored == document_with_two

    def test_get_batch_with_no_stock(self, uow, batch_store, document_with_none):
        batch_store.add(document_with_none)

        with uow:
            batch = uow.batches().get(document_with_none.document_id)

        assert batch.reference == "batch-0001"
        assert batch.batch_type == BatchType.PICKUP
        assert batch.stock == []

    def test_get_batch_with_one_stock(self, uow, batch_store, document_with_one):
        batch_store.add(document_with_one)

        with uow:
            batch = uow.batches().get(document_with_one.document_id)

        assert len(batch.stock) == 1
        assert batch.stock[0].species_reference == "species-0001"
        assert batch.stock[0].quantity == 20
        assert batch.stock[0].size == StockSize.TUBE

    def test_get_batch_with_two_stock(self, uow, batch_store, document_with_two):
        batch_store.add(document_with_two)

        with uow:
            batch = uow.batches().get(document_with_two.document_id)

        assert len(batch.stock) == 2
        assert batch.stock[0].species_reference == "species-0001"
        assert batch.stock[0].quantity == 20
        assert batch.stock[0].size == StockSize.TUBE

        assert batch.stock[1].species_reference == "species-0002"
        assert batch.stock[1].quantity == 5
        assert batch.stock[1].size == StockSize.POT
