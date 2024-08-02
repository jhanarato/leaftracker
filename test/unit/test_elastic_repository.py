import pytest

from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository, ElasticSourceOfStockRepository, \
    ElasticBatchRepository

from leaftracker.adapters.elasticsearch import Document
from leaftracker.domain.model import Species, TaxonName, SourceOfStock, SourceType, Batch, BatchType, Stock, StockSize
from fakes import FakeDocumentStore


@pytest.fixture
def store() -> FakeDocumentStore:
    return FakeDocumentStore("fake-index")


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


class TestSpeciesRepository:
    def test_add_without_reference(self, species_store, species_aggregate, species_document):
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

    def test_get(self, species_store, species_aggregate, species_document):
        repository = ElasticSpeciesRepository(species_store)
        repository.add(species_aggregate)
        repository.commit()

        retrieved = repository.get("species-0001")
        assert retrieved is not None
        assert retrieved.taxon_history.current() == TaxonName("Machaerina juncea")
        assert list(retrieved.taxon_history.previous()) == [TaxonName("Baumea juncea")]

    def test_get_missing(self, species_store, species_aggregate):
        repository = ElasticSpeciesRepository(species_store)
        repository.add(species_aggregate)
        assert repository.get("species-xxxx") is None

    def test_rollback(self, species_store, species_aggregate):
        repository = ElasticSpeciesRepository(species_store)
        repository.add(species_aggregate)
        repository.rollback()
        assert not repository.added()


@pytest.fixture
def source_repository(store) -> ElasticSourceOfStockRepository:
    return ElasticSourceOfStockRepository(store)


@pytest.fixture
def source_aggregate() -> SourceOfStock:
    return SourceOfStock(
        current_name="Trillion Trees",
        source_type=SourceType.NURSERY,
        reference="source-0001"
    )


@pytest.fixture
def source_document():
    return Document(
        document_id="source-0001",
        source={
            "current_name": "Trillion Trees",
            "source_type": "nursery",
        }
    )


class TestSourceRepository:
    def test_add(self, store, source_repository, source_aggregate, source_document):
        source_repository.add(source_aggregate)
        source_repository.commit()
        document = store.get("source-0001")
        assert document == source_document

    def test_get(self, store, source_repository, source_document):
        store.add(source_document)
        retrieved = source_repository.get("source-0001")
        assert retrieved
        assert retrieved.reference is not None

    def test_get_missing(self, store, source_repository):
        assert source_repository.get("No Such Source") is None

    def test_rollback(self, store, source_repository, source_aggregate):
        source_repository.add(source_aggregate)
        source_repository.rollback()
        assert not source_repository.added()


@pytest.fixture
def batch_repository(store) -> ElasticBatchRepository:
    return ElasticBatchRepository(store)


@pytest.fixture
def batch_aggregate() -> Batch:
    batch = Batch("source-0001", BatchType.PICKUP, "batch-0001")
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
    def test_add(self, store, batch_repository, batch_aggregate, batch_document):
        batch_repository.add(batch_aggregate)
        batch_repository.commit()
        document = store.get("batch-0001")
        assert document == batch_document

    def test_get(self, store, batch_repository, batch_document):
        store.add(batch_document)
        retrieved = batch_repository.get("batch-0001")
        assert retrieved
        assert retrieved.reference is not None

    def test_get_missing(self, store, batch_repository):
        assert batch_repository.get("No Such Source") is None

    def test_rollback(self, store, batch_repository, batch_aggregate):
        batch_repository.add(batch_aggregate)
        batch_repository.rollback()
        assert not batch_repository.added()
