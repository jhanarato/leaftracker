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


class TestElasticSpeciesRepository:
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

    def test_add_two_without_references(self, species_store, species_document):
        repository = ElasticSpeciesRepository(species_store)
        repository.add(Species("Acacia saligna"))
        repository.add(Species("Acacia dentifera"))
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


class TestSourceRepository:
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
