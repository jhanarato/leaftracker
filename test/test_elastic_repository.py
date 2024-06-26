import pytest

from conftest import INDEX_TEST_PREFIX
from leaftracker.adapters.elastic_index import Document
from leaftracker.adapters.elastic_repository import (
    SpeciesRepository, SPECIES_INDEX,
    species_to_document, document_to_species
)
from leaftracker.domain.model import Species, TaxonName


@pytest.fixture
def repository() -> SpeciesRepository:
    repo = SpeciesRepository(INDEX_TEST_PREFIX + SPECIES_INDEX)
    repo.index.delete_all_documents()
    return repo


def test_should_add_taxon_history_to_document():
    species = Species(current_name="Machaerina juncea", reference="species-0001")

    species.taxon_history.add_previous_name("Baumea juncea")

    document = species_to_document(species)

    assert document == Document(
        document_id="species-0001",
        source={
            "scientific_names": [
                {"genus": "Baumea", "species": "juncea"},
                {"genus": "Machaerina", "species": "juncea"},
            ]
        }
    )


def test_should_add_taxon_history_to_domain_object():
    document = Document(
        document_id="species-0001",
        source={
            "scientific_names": [
                {"genus": "Baumea", "species": "juncea"},
                {"genus": "Machaerina", "species": "juncea"},
            ]
        }
    )

    result = document_to_species(document)

    assert result.taxon_history.current() == TaxonName("Machaerina juncea")
    assert list(result.taxon_history.previous()) == [TaxonName("Baumea juncea")]


class TestSpeciesRepository:
    def test_should_indicate_missing_document(self, repository):
        assert repository.get("Nothing") is None

    def test_should_rollback(self, repository, saligna):
        repository.add(saligna)
        repository.rollback()
        assert not repository.added()
