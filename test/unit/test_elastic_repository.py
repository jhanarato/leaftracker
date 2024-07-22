import pytest

from leaftracker.adapters.elastic_repository import (
    ElasticSpeciesRepository, species_to_document, document_to_species
)
from leaftracker.adapters.elasticsearch import Document
from leaftracker.domain.model import Species, TaxonName
from unit.fakes import FakeDocumentStore


@pytest.fixture
def species_repository() -> ElasticSpeciesRepository:
    store = FakeDocumentStore("fake-index")
    repository = ElasticSpeciesRepository(store)
    return repository


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

        assert retrieved_aggregate.taxon_history.current() == TaxonName("Machaerina juncea")
        assert list(retrieved_aggregate.taxon_history.previous()) == [TaxonName("Baumea juncea")]

    def test_get_missing(self, species_repository):
        assert species_repository.get("no-such-species") is None

    def test_rollback(self, species_repository, saligna):
        species_repository.add(saligna)
        species_repository.rollback()
        assert not species_repository.added()
