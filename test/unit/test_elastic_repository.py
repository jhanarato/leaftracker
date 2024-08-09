import pytest

from fakes import FakeDocumentStore
from leaftracker.adapters.elastic.repository import (
    ElasticSpeciesRepository,
    ElasticSourceOfStockRepository,
    ElasticBatchRepository, AggregateWriter
)
from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.domain.model import Species, SourceOfStock, SourceType, Batch, BatchType, Stock, StockSize


@pytest.fixture
def species_aggregate() -> Species:
    species = Species(current_name="Machaerina juncea", reference="species-0001")
    species.taxon_history.add_previous_name("Baumea juncea")
    return species


@pytest.fixture
def species_document() -> Document:
    return Document(
        document_id="species-0001",
        source={
            "current_scientific_name": "Machaerina juncea",
            "previous_scientific_names": ["Baumea juncea"]
        }
    )


class TestElasticSpeciesRepository:
    def test_add_without_reference(self, species_store, species_aggregate, species_document):
        species_aggregate.reference = None
        repository = ElasticSpeciesRepository(species_store)
        repository.add(species_aggregate)
        repository.commit()

        document = species_store.get("species-0001")
        assert document == species_document

    def test_add_with_reference(self, species_store, species_aggregate, species_document):
        species_aggregate.reference = "species-yyyy"
        repository = ElasticSpeciesRepository(species_store)
        repository.add(species_aggregate)
        repository.commit()

        document = species_store.get("species-yyyy")
        assert document.document_id == "species-yyyy"

    def test_add_two_without_references(self, species_store, species_document):
        repository = ElasticSpeciesRepository(species_store)
        repository.add(Species("Acacia saligna", None))
        repository.add(Species("Acacia dentifera", None))
        repository.commit()
        assert species_store.ids() == ["species-0001", "species-0002"]

    def test_get_existing(self, species_store, species_aggregate, species_document):
        repository = ElasticSpeciesRepository(species_store)
        repository.add(species_aggregate)
        repository.commit()

        retrieved = repository.get("species-0001")
        assert retrieved is not None

    def test_get_missing(self, species_store, species_aggregate):
        repository = ElasticSpeciesRepository(species_store)
        repository.add(species_aggregate)
        assert repository.get("species-xxxx") is None

    def test_commit_assigns_reference_to_aggregate(self, species_store):
        aggregate = Species("Acacia saligna", None)
        repository = ElasticSpeciesRepository(species_store)
        repository.add(aggregate)
        repository.commit()
        assert aggregate.reference == "species-0001"

    def test_rollback(self, species_store, species_aggregate):
        repository = ElasticSpeciesRepository(species_store)
        repository.add(species_aggregate)
        repository.rollback()
        assert not repository.added()


@pytest.fixture
def source_repository(source_store) -> ElasticSourceOfStockRepository:
    return ElasticSourceOfStockRepository(source_store)


@pytest.fixture
def source_aggregate() -> SourceOfStock:
    return SourceOfStock(
        current_name="Trillion Trees",
        source_type=SourceType.NURSERY,
        reference="source_of_stock-0001"
    )


@pytest.fixture
def source_document():
    return Document(
        document_id="source_of_stock-0001",
        source={
            "current_name": "Trillion Trees",
            "source_type": "nursery",
        }
    )


class TestSourceOfStockRepository:
    def test_add_without_reference(self, source_store, source_aggregate, source_document):
        repository = ElasticSourceOfStockRepository(source_store)
        repository.add(source_aggregate)
        repository.commit()

        document = source_store.get("source_of_stock-0001")
        assert document == source_document

    def test_add_with_reference(self, source_store, source_aggregate, source_document):
        source_aggregate.reference = "source-yyyy"
        repository = ElasticSourceOfStockRepository(source_store)
        repository.add(source_aggregate)
        repository.commit()

        document = source_store.get("source-yyyy")
        assert document.document_id == "source-yyyy"

    def test_add_two_without_references(self, source_store, source_document):
        repository = ElasticSourceOfStockRepository(source_store)
        repository.add(SourceOfStock("Trillion Trees", SourceType.NURSERY))
        repository.add(SourceOfStock("APACE", SourceType.NURSERY))
        repository.commit()
        assert source_store.ids() == ['source_of_stock-0001', 'source_of_stock-0002']
        
    def test_get_existing(self, source_store, source_aggregate, source_document):
        repository = ElasticSourceOfStockRepository(source_store)
        repository.add(source_aggregate)
        repository.commit()

        retrieved = repository.get("source_of_stock-0001")
        assert retrieved is not None
        
    def test_get_missing(self, source_store, source_aggregate):
        repository = ElasticSourceOfStockRepository(source_store)
        repository.add(source_aggregate)
        assert repository.get("source-xxxx") is None

    def test_commit_assigns_reference_to_aggregate(self, source_store):
        aggregate = SourceOfStock("Trillion Trees", SourceType.NURSERY, None)
        repository = ElasticSourceOfStockRepository(source_store)
        repository.add(aggregate)
        repository.commit()
        assert aggregate.reference == "source_of_stock-0001"

    def test_rollback(self, source_store, source_aggregate):
        repository = ElasticSourceOfStockRepository(source_store)
        repository.add(source_aggregate)
        repository.rollback()
        assert not repository.added()


@pytest.fixture
def batch_repository(batch_store) -> ElasticBatchRepository:
    return ElasticBatchRepository(batch_store)


@pytest.fixture
def batch_aggregate() -> Batch:
    batch = Batch("source-0001", BatchType.PICKUP, "batch-0001")
    batch.add(Stock("species-0001", 20, StockSize.TUBE))
    batch.add(Stock("species-0002", 5, StockSize.POT))
    return batch


@pytest.fixture
def batch_aggregate_2() -> Batch:
    batch = Batch("source-0001", BatchType.PICKUP, "batch-0002")
    batch.add(Stock("species-0001", 20, StockSize.TUBE))
    batch.add(Stock("species-0002", 5, StockSize.POT))
    return batch


@pytest.fixture
def batch_document():
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


class TestBatchRepository:
    def test_add_without_reference(self, batch_store, batch_aggregate, batch_document):
        repository = ElasticBatchRepository(batch_store)
        repository.add(batch_aggregate)
        repository.commit()

        document = batch_store.get("batch-0001")
        assert document == batch_document

    def test_add_with_reference(self, batch_store, batch_aggregate, batch_document):
        batch_aggregate.reference = "batch-yyyy"
        repository = ElasticBatchRepository(batch_store)
        repository.add(batch_aggregate)
        repository.commit()

        document = batch_store.get("batch-yyyy")
        assert document.document_id == "batch-yyyy"

    def test_add_two_without_references(self, batch_store, batch_document, batch_aggregate, batch_aggregate_2):
        repository = ElasticBatchRepository(batch_store)
        repository.add(batch_aggregate)
        repository.add(batch_aggregate_2)
        repository.commit()
        assert batch_store.ids() == ['batch-0001', 'batch-0002']

    def test_get_existing(self, batch_store, batch_aggregate, batch_document):
        repository = ElasticBatchRepository(batch_store)
        repository.add(batch_aggregate)
        repository.commit()

        retrieved = repository.get("batch-0001")
        assert retrieved is not None

    def test_get_missing(self, batch_store, batch_aggregate):
        repository = ElasticBatchRepository(batch_store)
        repository.add(batch_aggregate)
        assert repository.get("batch-xxxx") is None

    def test_commit_assigns_reference_to_aggregate(self, batch_store, batch_aggregate):
        batch_aggregate.reference = None
        repository = ElasticBatchRepository(batch_store)
        repository.add(batch_aggregate)
        repository.commit()
        assert batch_aggregate.reference == "batch-0001"

    def test_rollback(self, batch_store, batch_aggregate):
        repository = ElasticBatchRepository(batch_store)
        repository.add(batch_aggregate)
        repository.rollback()
        assert not repository.added()


class Aggregate:
    def __init__(self, number: int, reference: str):
        self.reference = reference
        self.number = number


def to_document(aggregate: Aggregate) -> Document:
    return Document(aggregate.reference, {"number": aggregate.number})


@pytest.fixture
def aggregate() -> Aggregate:
    return Aggregate(123, "agg-0001")


@pytest.fixture
def document() -> Document:
    return Document("agg-0001", {"number": 123})


@pytest.fixture
def store() -> FakeDocumentStore:
    return FakeDocumentStore("agg")

@pytest.fixture
def writer(store) -> AggregateWriter:
    return AggregateWriter[Aggregate](store, to_document)


class TestAggregateWriter:
    def test_add_pending_change(self, writer, aggregate):
        writer.add(aggregate)
        assert list(writer.added()) == [aggregate]

    def test_discards_added_after_write(self, writer, aggregate):
        writer.add(aggregate)
        writer.write()
        assert list(writer.added()) == []

    def test_writes_to_document(self, writer, store, aggregate, document):
        writer.add(aggregate)
        writer.write()

        assert store.get("agg-0001") == document
