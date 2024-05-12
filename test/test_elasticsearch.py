import pytest
from elasticsearch import Elasticsearch

from leaftracker.adapters.elastic_repository import SpeciesRepository, Index
from leaftracker.domain.model import Species, ScientificName
from leaftracker.service_layer.elastic_uow import ElasticUnitOfWork


@pytest.fixture
def repository() -> SpeciesRepository:
    repo = SpeciesRepository()
    repo.index.create()
    repo.index.delete_all_documents()
    return repo


@pytest.fixture
def species_index() -> Index:
    return SpeciesRepository().index


@pytest.fixture
def populate(species_index, species) -> None:
    repo = SpeciesRepository()
    _ = repo.add(species)
    species_index.refresh()


class TestIndex:
    def test_should_create_missing_index(self, species_index):
        species_index.delete()
        assert not species_index.exists()
        species_index.create()
        assert species_index.exists()

    def test_should_not_overwrite(self, species_index, populate):
        assert species_index.count() == 1
        species_index.create()
        assert species_index.count() == 1

    def test_should_delete_missing(self, species_index):
        species_index.delete()
        assert not species_index.exists()
        species_index.delete()
        assert not species_index.exists()

    def test_should_delete_existing(self, species_index):
        species_index.create()
        species_index.delete()
        assert not species_index.exists()

    def test_should_delete_documents(self, species_index, populate):
        assert species_index.count() == 1
        species_index.delete_all_documents()
        species_index.refresh()
        assert species_index.count() == 0


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
        assert species.reference is None
        repository.add(species)
        assert species.reference is not None

    def test_should_get(self, repository, species):
        repository.add(species)
        got = repository.get(species.reference)
        assert got.reference == species.reference


class TestElasticUnitOfWork:
    def test_should_commit_a_change(self, species):
        uow = ElasticUnitOfWork()

        with uow:
            uow.species().add(species)

        got = uow.species().get(species.reference)
        assert got.reference == species.reference
