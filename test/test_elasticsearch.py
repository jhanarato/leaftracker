import pytest
from elasticsearch import Elasticsearch

from leaftracker.adapters.elastic_repository import SpeciesRepository, Index
from leaftracker.domain.model import Species, ScientificName


@pytest.fixture
def acacia() -> ScientificName:
    return ScientificName(
        genus="Acacia",
        species="Saligna",
        is_most_recent=True
    )


@pytest.fixture
def new_repo() -> SpeciesRepository:
    repo = SpeciesRepository()
    repo._index.delete()
    repo._index.create()
    return repo


@pytest.fixture
def index() -> Index:
    name = "species"
    mappings = {
        "properties": {
            "genus": {"type": "text"},
            "species": {"type": "text"},
        }
    }

    return Index(name, mappings)


@pytest.fixture
def populate(index, acacia) -> None:
    repo = SpeciesRepository()
    _ = repo.add(Species(acacia))
    index.refresh()


class TestIndex:
    def test_should_create_missing_index(self, index):
        index.delete()
        assert not index.exists()
        index.create()
        assert index.exists()

    def test_should_not_overwrite(self, index, populate):
        assert index.count() == 1
        index.create()
        assert index.count() == 1

    def test_should_delete_missing(self, index):
        index.delete()
        assert not index.exists()
        index.delete()
        assert not index.exists()

    def test_should_delete_existing(self, index):
        index.create()
        index.delete()
        assert not index.exists()

    def test_should_delete_documents(self, index, populate):
        assert index.count() == 1
        index.delete_all_documents()
        index.refresh()
        assert index.count() == 0


class TestSpeciesRepository:
    def test_should_add(self, new_repo, acacia):
        species = Species(acacia)
        reference = new_repo.add(species)
        assert reference == species.reference

    def test_should_get(self, new_repo, acacia):
        reference = new_repo.add(Species(acacia))
        species = new_repo.get(reference)
        assert species.reference == reference
