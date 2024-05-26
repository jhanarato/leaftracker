import pytest
from elasticsearch import Elasticsearch

from leaftracker.adapters.elastic_index import Index
from leaftracker.adapters.elastic_repository import SpeciesRepository
from leaftracker.domain.model import Species, ScientificName
from leaftracker.service_layer.elastic_uow import ElasticUnitOfWork


@pytest.fixture(autouse=True, scope='session')
def delete_test_indexes():
    yield
    es = Elasticsearch(hosts="http://localhost:9200")
    es.indices.delete(index=["test_index", "test_species"])


@pytest.fixture
def saligna() -> Species:
    return Species(
        ScientificName(
            genus="Acacia",
            species="Saligna",
            is_most_recent=True
        )
    )


@pytest.fixture
def dentifera() -> Species:
    return Species(
        ScientificName(
            genus="Acacia",
            species="Dentifera",
            is_most_recent=True
        )
    )


@pytest.fixture
def repository() -> SpeciesRepository:
    repo = SpeciesRepository(use_test_index=True)
    repo.index.delete_all_documents()
    return repo


@pytest.fixture
def species_index() -> Index:
    repo = SpeciesRepository(use_test_index=True)
    return repo.index


@pytest.fixture
def added_species(species_index, saligna) -> Species:
    uow = ElasticUnitOfWork(use_test_indexes=True)

    with uow:
        uow.species().add(saligna)
        uow.commit()

    return saligna


class TestSpeciesRepository:
    def test_should_indicate_missing_document(self, repository):
        assert repository.get("Nothing") is None

    def test_should_queue_documents_to_commit(self, repository, saligna):
        repository.add(saligna)
        assert len(repository.queued()) == 1

    def test_should_clear_queue(self, repository, saligna):
        repository.add(saligna)
        repository.clear_queue()
        assert not repository.queued()


@pytest.fixture
def uow() -> ElasticUnitOfWork:
    uow = ElasticUnitOfWork(use_test_indexes=True)
    uow.species().index.delete_all_documents()
    return uow


class TestElasticUnitOfWork:
    def test_should_rollback_if_not_committed(self, uow, saligna):
        with uow:
            uow.species().add(saligna)

        assert saligna.reference is None

    def test_should_commit(self, uow, saligna):
        with uow:
            uow.species().add(saligna)
            uow.commit()

        assert saligna.reference is not None

    def test_should_add_two_species(self, uow, saligna, dentifera):
        with uow:
            uow.species().add(saligna)
            uow.species().add(dentifera)
            uow.commit()

        assert uow.species().index.document_count() == 2

    def test_should_clear_queue_on_rollback(self, uow, saligna):
        with uow:
            uow.species().add(saligna)

        assert not uow.species().queued()

    def test_should_rollback_explicitly(self, uow, saligna):
        with uow:
            uow.species().add(saligna)
            uow.rollback()
            assert not uow.species().queued()

    def test_should_clear_queue_after_commit(self, uow, saligna):
        with uow:
            uow.species().add(saligna)
            uow.commit()
            assert not uow.species().queued()

    def test_should_get_all_indexes(self, uow):
        index_names = [index.name for index in uow.indexes()]
        assert index_names == ["test_species"]


class TestTestIndicies:
    def test_should_normally_use_production_index(self):
        uow = ElasticUnitOfWork(use_test_indexes=False)
        assert uow.species().index.name == "species"

    def test_should_use_test_index(self):
        uow = ElasticUnitOfWork(use_test_indexes=True)
        assert uow.species().index.name == "test_species"
