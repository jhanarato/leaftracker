import pytest
from elasticsearch import Elasticsearch

from leaftracker.adapters.elastic_repository import SpeciesRepository, Index
from leaftracker.domain.model import Species, ScientificName


@pytest.fixture
def repository() -> SpeciesRepository:
    repo = SpeciesRepository()
    repo._index.delete()
    repo._index.create()
    return repo


@pytest.fixture
def index() -> Index:
    return SpeciesRepository()._index


@pytest.fixture
def populate(index, species) -> None:
    repo = SpeciesRepository()
    _ = repo.add(species)
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


@pytest.fixture
def species() -> Species:
    return Species(
        ScientificName(
            genus="Acacia",
            species="Saligna",
            is_most_recent=True
        )
    )


class TestSpeciesRepository:
    def test_should_add(self, repository, species):
        reference = repository.add(species)
        assert reference == species.reference

    def test_should_get(self, repository, species):
        reference = repository.add(species)
        got = repository.get(reference)
        assert got.reference == reference
