import pytest
from elasticsearch import Elasticsearch

from leaftracker.adapters.elastic_repository import SpeciesRepository
from leaftracker.domain.model import Species, ScientificName


@pytest.fixture
def acacia() -> ScientificName:
    return ScientificName(
        genus="Acacia",
        species="Saligna",
        is_most_recent=True
    )


@pytest.fixture
def es() -> Elasticsearch:
    return Elasticsearch(hosts="http://localhost:9200")


@pytest.fixture
def new_repo() -> SpeciesRepository:
    repo = SpeciesRepository()
    repo.delete_index()
    repo.create_index()
    return repo


class TestSpeciesRepository:
    def test_should_create_new_index(self, es):
        repo = SpeciesRepository()
        es.options(ignore_status=404).indices.delete(index=repo.index)
        repo.create_index()
        assert repo.index_exists()

    def test_should_not_overwrite_repo_when_creating_index(self, es, acacia):
        repo = SpeciesRepository()
        reference = repo.add(Species(acacia))
        repo.create_index()
        repo.refresh()
        assert repo.get(reference)

    def test_should_delete_missing_index(self, es):
        repo = SpeciesRepository()
        repo.delete_index()
        repo.delete_index()
        assert not es.indices.exists(index=repo.index)

    def test_should_delete_existing_index(self, es):
        repo = SpeciesRepository()
        repo.create_index()
        repo.delete_index()
        assert not es.indices.exists(index=repo.index)

    def test_should_add_a_species(self, new_repo, acacia, es):
        reference = new_repo.add(Species(acacia))
        assert es.exists(index=new_repo.index, id=reference)

    def test_should_get_a_species(self, new_repo, acacia):
        reference = new_repo.add(Species(acacia))
        species = new_repo.get(reference)
        assert species.reference == reference

    def test_should_generate_reference_if_none_provided(self, new_repo, acacia, es):
        species = Species(acacia)
        reference = new_repo.add(species)
        assert reference is not None

    def test_should_delete_all_documents(self, new_repo, acacia, es):
        species = Species(acacia)
        _ = new_repo.add(species)
        new_repo.refresh()
        assert new_repo.count() == 1
        new_repo.delete_all_documents()
        new_repo.refresh()
        assert new_repo.count() == 0
