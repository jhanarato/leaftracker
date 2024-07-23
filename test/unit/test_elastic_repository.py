import pytest

from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository, ElasticSourceRepository

from leaftracker.adapters.elasticsearch import Document
from leaftracker.domain.model import Species, TaxonName
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
def source_repository(store) -> ElasticSourceRepository:
    return ElasticSourceRepository(store)


@pytest.fixture
def source_aggregate():
    pass


@pytest.fixture
def source_document():
    pass


class TestSourceRepository:
    def test_add(self, store, source_repository, source_aggregate, source_document):
        pass
