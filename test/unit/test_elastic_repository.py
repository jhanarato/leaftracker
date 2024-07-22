import pytest

from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository

from leaftracker.adapters.elasticsearch import Document
from leaftracker.domain.model import Species, TaxonName
from unit.fakes import FakeDocumentStore # type: ignore


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


class TestSpeciesRepository:
    def test_store_species(self, species_aggregate, species_document):
        store = FakeDocumentStore("fake-index")
        repository = ElasticSpeciesRepository(store)
        repository.add(species_aggregate)
        repository.commit()
        document = store.get("species-0001")
        assert document == species_document

    def test_retrieve_species(self, species_aggregate):
        store = FakeDocumentStore("fake-index")
        repository = ElasticSpeciesRepository(store)
        repository.add(species_aggregate)
        repository.commit()
        retrieved_aggregate = repository.get("species-0001")

        assert retrieved_aggregate
        assert retrieved_aggregate.taxon_history.current() == TaxonName("Machaerina juncea")
        assert list(retrieved_aggregate.taxon_history.previous()) == [TaxonName("Baumea juncea")]

    def test_get_missing(self):
        store = FakeDocumentStore("fake-index")
        repository = ElasticSpeciesRepository(store)
        assert repository.get("no-such-species") is None

    def test_rollback(self, species_aggregate):
        store = FakeDocumentStore("fake-index")
        repository = ElasticSpeciesRepository(store)
        repository.add(species_aggregate)
        repository.rollback()
        assert not repository.added()
