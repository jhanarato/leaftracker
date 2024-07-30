import pytest

from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository, ElasticSourceOfStockRepository

from leaftracker.adapters.elasticsearch import Document
from leaftracker.domain.model import Species, TaxonName, SourceOfStock, SourceType
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


@pytest.fixture
def species_repository(store) -> ElasticSpeciesRepository:
    return ElasticSpeciesRepository(store)


class TestSpeciesRepository:
    def test_add(self, store, species_repository, species_aggregate, species_document):
        species_repository.add(species_aggregate)
        species_repository.commit()
        document = store.get("species-0001")
        assert document == species_document

    def test_get(self, store, species_repository, species_document):
        store.add(species_document)
        retrieved = species_repository.get("species-0001")

        assert retrieved
        assert retrieved.taxon_history.current() == TaxonName("Machaerina juncea")
        assert list(retrieved.taxon_history.previous()) == [TaxonName("Baumea juncea")]

    def test_get_missing(self, store, species_repository):
        assert species_repository.get("no-such-species") is None

    def test_rollback(self, store, species_repository, species_aggregate):
        species_repository.add(species_aggregate)
        species_repository.rollback()
        assert not species_repository.added()


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

    def test_get_missing(self, store, source_repository):
        assert source_repository.get("No Such Source") is None

    def test_rollback(self, store, source_repository, source_aggregate):
        source_repository.add(source_aggregate)
        source_repository.rollback()
        assert not source_repository.added()
