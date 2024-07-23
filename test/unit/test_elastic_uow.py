import pytest

from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository
from leaftracker.service_layer.elastic_uow import ElasticUnitOfWork
from fakes import FakeDocumentStore


@pytest.fixture
def store() -> FakeDocumentStore:
    return FakeDocumentStore("fake-index")


@pytest.fixture
def repository(store) -> ElasticSpeciesRepository:
    return ElasticSpeciesRepository(store)


@pytest.fixture
def uow(repository) -> ElasticUnitOfWork:
    uow = ElasticUnitOfWork(repository)
    return uow


def test_should_rollback_if_not_committed(uow, saligna):
    with uow:
        uow.species().add(saligna)

    assert saligna.reference is None


def test_should_commit(uow, saligna):
    with uow:
        uow.species().add(saligna)
        uow.commit()

    assert saligna.reference is not None


def test_should_add_two_species(uow, saligna, dentifera):
    with uow:
        uow.species().add(saligna)
        uow.species().add(dentifera)
        uow.commit()

    assert saligna.reference is not None
    assert dentifera.reference is not None
    assert saligna.reference != dentifera.reference


def test_should_clear_queue_on_rollback(uow, repository, saligna):
    with uow:
        uow.species().add(saligna)

    assert not repository.added()


def test_should_rollback_explicitly(uow, repository, saligna):
    with uow:
        uow.species().add(saligna)
        uow.rollback()

    assert not repository.added()


def test_should_clear_queue_after_commit(uow, repository, saligna):
    with uow:
        uow.species().add(saligna)
        uow.commit()

    assert not repository.added()
