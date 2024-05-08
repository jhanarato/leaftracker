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
    repo._index.delete()
    repo._index.create()
    return repo


class TestSpeciesRepository:
    def test_should_create_new_index(self, es):
        repo = SpeciesRepository()
        repo._index.delete()
        assert not repo._index.exists()
        repo._index.create()
        assert repo._index.exists()

    def test_should_not_overwrite_repo_when_creating_index(self, es, acacia):
        repo = SpeciesRepository()
        reference = repo.add(Species(acacia))
        repo._index.create()
        repo._index.refresh()
        assert repo.get(reference)

    def test_should_delete_when_missing(self, es):
        repo = SpeciesRepository()
        repo._index.delete()
        assert not repo._index.exists()
        repo._index.delete()
        assert not repo._index.exists()

    def test_should_delete_existing_index(self, es):
        repo = SpeciesRepository()
        repo._index.create()
        repo._index.delete()
        assert not repo._index.exists()

    def test_should_add_a_species(self, new_repo, acacia, es):
        reference = new_repo.add(Species(acacia))
        # TODO Implement this as SpeciesRepository.__contains__
        assert es.exists(index=new_repo._index.name, id=reference)

    def test_should_generate_reference_if_none_provided(self, new_repo, acacia, es):
        species = Species(acacia)
        reference = new_repo.add(species)
        assert reference == species.reference

    def test_should_assign_reference_to_species_on_add(self, new_repo, acacia):
        species = Species(acacia)
        new_repo.add(species)
        assert species.reference is not None

    def test_should_get_a_species(self, new_repo, acacia):
        reference = new_repo.add(Species(acacia))
        species = new_repo.get(reference)
        assert species.reference == reference

    def test_should_delete_all_documents(self, new_repo, acacia, es):
        species = Species(acacia)
        _ = new_repo.add(species)
        new_repo._index.refresh()
        assert new_repo._index.count() == 1
        new_repo._index.delete_all_documents()
        new_repo._index.refresh()
        assert new_repo._index.count() == 0
