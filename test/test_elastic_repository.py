import pytest

from conftest import INDEX_TEST_PREFIX
from leaftracker.adapters.elastic_index import Document
from leaftracker.adapters.elastic_repository import SpeciesRepository, SPECIES_INDEX, species_to_document, \
    document_to_species
from leaftracker.domain.model import Species, TaxonName


@pytest.fixture
def repository() -> SpeciesRepository:
    repo = SpeciesRepository(INDEX_TEST_PREFIX + SPECIES_INDEX)
    repo.index.delete_all_documents()
    return repo


def test_should_add_taxon_history_to_document():
    species = Species(
        name=TaxonName("XXX", "YYY"),
        reference="species-0001"
    )

    species.taxon_history.new_name("Baumea juncea")
    species.taxon_history.new_name("Machaerina juncea")

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


def test_should_add_scientfic_names_to_domain_object():
    document = Document(
        document_id="species-0001",
        source={
            "scientific_names": [
                {"genus": "Baumea", "species": "juncea"},
                {"genus": "Machaerina", "species": "juncea"},
            ]
        }
    )

    expected = Species(name=TaxonName("Baumea", "juncea"), reference="species-0001")
    expected.new_taxon_name(TaxonName("Machaerina", "juncea"))
    expected.taxon_history.new_name("Machaerina juncea")

    result = document_to_species(document)

    assert expected.taxon_names == result.taxon_names


class TestSpeciesRepository:
    def test_should_indicate_missing_document(self, repository):
        assert repository.get("Nothing") is None

    def test_should_rollback(self, repository, saligna):
        repository.add(saligna)
        repository.rollback()
        assert not repository.added()
