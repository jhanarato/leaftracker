import pytest

from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository

from leaftracker.adapters.elasticsearch import Document
from leaftracker.domain.model import Species, TaxonName
from fakes import FakeDocumentStore


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
            "scientific_names": [
                {"genus": "Baumea", "species": "juncea"},
                {"genus": "Machaerina", "species": "juncea"},
            ]
        }
    )


@pytest.fixture
def store() -> FakeDocumentStore:
    return FakeDocumentStore("fake-index")


@pytest.fixture
def repository(store) -> ElasticSpeciesRepository:
    return ElasticSpeciesRepository(store)


class TestSpeciesRepository:
    def test_add(self, store, repository, species_aggregate, species_document):
        repository.add(species_aggregate)
        repository.commit()
        document = store.get("species-0001")
        assert document == species_document

    def test_get(self, store, repository, species_aggregate):
        repository.add(species_aggregate)
        repository.commit()
        retrieved_aggregate = repository.get("species-0001")

        assert retrieved_aggregate
        assert retrieved_aggregate.taxon_history.current() == TaxonName("Machaerina juncea")
        assert list(retrieved_aggregate.taxon_history.previous()) == [TaxonName("Baumea juncea")]

    def test_get_missing(self, store, repository):
        assert repository.get("no-such-species") is None

    def test_rollback(self, store, repository, species_aggregate):
        repository.add(species_aggregate)
        repository.rollback()
        assert not repository.added()
