import pytest

from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.domain.model import SourceOfStock, SourceType


@pytest.fixture
def aggregate() -> SourceOfStock:
    return SourceOfStock(
        current_name="Trillion Trees",
        source_type=SourceType.NURSERY,
        reference="source_of_stock-0001"
    )


@pytest.fixture
def document():
    return Document(
        document_id="source_of_stock-0001",
        source={
            "current_name": "Trillion Trees",
            "source_type": "nursery",
        }
    )


class TestElasticSourceOfStockRepository:
    def test_add(self, uow, source_store, aggregate, document):
        with uow:
            uow.sources().add(aggregate)
            uow.commit()

        stored = source_store.get(document.document_id)
        assert stored == document
