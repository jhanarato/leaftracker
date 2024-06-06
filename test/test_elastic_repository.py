import pytest

from conftest import INDEX_TEST_PREFIX
from leaftracker.adapters.elastic_index import Document
from leaftracker.adapters.elastic_repository import SpeciesRepository, SPECIES_INDEX, new_species_to_document
from leaftracker.domain.model import Species, ScientificName


@pytest.fixture
def repository() -> SpeciesRepository:
    repo = SpeciesRepository(INDEX_TEST_PREFIX + SPECIES_INDEX)
    repo.index.delete_all_documents()
    return repo


def test_should_add_scientific_names_to_document():
    species = Species(ScientificName("Baumea", "juncea"))
    species.new_scientific_name(ScientificName("Machaerina", "juncea"))
    document = new_species_to_document(species)
    assert document == Document(
        document_id=None,
        source={
            "scientific_names": [
                {"genus": "Baumea", "species": "juncea"},
                {"genus": "Machaerina", "species": "juncea"},
            ]
        }
    )


class TestSpeciesRepository:
    def test_should_indicate_missing_document(self, repository):
        assert repository.get("Nothing") is None

    def test_should_rollback(self, repository, saligna):
        repository.add(saligna)
        repository.rollback()
        assert not repository.added()
